from __future__ import annotations 

import random 
from typing import List 

from django .contrib .auth .models import User 
from django .contrib .auth .hashers import make_password 
from django .core .management .base import BaseCommand ,CommandError 
from django .db import transaction 

from questions .models import Answer ,AnswerLike ,Profile ,Question ,QuestionLike ,Tag 


class Command (BaseCommand ):
    help ="Fill database with test data. Usage: python manage.py fill_db [ratio]"

    def add_arguments (self ,parser ):
        parser .add_argument ("ratio",nargs ="?",type =int ,default =100 )

    @transaction .atomic 
    def handle (self ,*args ,**options ):
        ratio :int =options .get ("ratio")
        if ratio <=0 :
            raise CommandError ("ratio must be a positive integer")

        num_users =ratio 
        num_tags =ratio 
        num_questions =ratio *10 
        num_answers =ratio *100 
        num_votes =ratio *200 

        self .stdout .write (self .style .NOTICE (
        f"Creating users={num_users}, tags={num_tags}, questions={num_questions}, answers={num_answers}, votes={num_votes}"
        ))


        base_user_count =User .objects .count ()
        password_hash =make_password ("password")

        users :List [User ]=[]
        for i in range (1 ,num_users +1 ):
            n =base_user_count +i 
            users .append (
            User (
            username =f"user{n}",
            email =f"user{n}@example.com",
            password =password_hash ,
            )
            )
        User .objects .bulk_create (users ,batch_size =10_000 )

        created_users =list (User .objects .order_by ("id").values_list ("id",flat =True ))[-num_users :]

        profiles :List [Profile ]=[]
        for idx ,user_id in enumerate (created_users ,start =1 ):
            n =base_user_count +idx 
            profiles .append (Profile (user_id =user_id ,nickname =f"User {n}"))
        Profile .objects .bulk_create (profiles ,batch_size =10_000 )


        base_tag_count =Tag .objects .count ()
        tags :List [Tag ]=[]
        for i in range (1 ,num_tags +1 ):
            n =base_tag_count +i 
            tags .append (Tag (name =f"tag{n}"))
        Tag .objects .bulk_create (tags ,batch_size =10_000 )
        tag_ids =list (Tag .objects .order_by ("id").values_list ("id",flat =True ))[-num_tags :]


        questions :List [Question ]=[]
        for i in range (1 ,num_questions +1 ):
            author_id =random .choice (created_users )
            questions .append (
            Question (
            author_id =author_id ,
            title =f"Question title {i}",
            text =f"Question text {i}. Lorem ipsum dolor sit amet.",
            rating =random .randint (-5 ,50 ),
            )
            )
        Question .objects .bulk_create (questions ,batch_size =10_000 )
        question_ids =list (Question .objects .order_by ("id").values_list ("id",flat =True ))[-num_questions :]


        through =Question .tags .through 
        m2m_rows =[]
        for qid in question_ids :
            for tid in random .sample (tag_ids ,k =random .randint (1 ,min (3 ,len (tag_ids )))):
                m2m_rows .append (through (question_id =qid ,tag_id =tid ))
        through .objects .bulk_create (m2m_rows ,batch_size =50_000 ,ignore_conflicts =True )


        answers :List [Answer ]=[]
        for i in range (1 ,num_answers +1 ):
            qid =random .choice (question_ids )
            author_id =random .choice (created_users )
            answers .append (
            Answer (
            question_id =qid ,
            author_id =author_id ,
            text =f"Answer text {i}.",
            rating =random .randint (-3 ,30 ),
            is_correct =False ,
            )
            )
        Answer .objects .bulk_create (answers ,batch_size =20_000 )
        answer_ids =list (Answer .objects .order_by ("id").values_list ("id",flat =True ))[-num_answers :]



        for qid in question_ids [:min (5_000 ,len (question_ids ))]:
            aid =random .choice (answer_ids )
            Answer .objects .filter (pk =aid ,question_id =qid ).update (is_correct =True )


        qlikes :List [QuestionLike ]=[]
        alikes :List [AnswerLike ]=[]
        for _ in range (num_votes ):
            user_id =random .choice (created_users )
            value =1 if random .random ()<0.7 else -1 
            if random .random ()<0.5 :
                qlikes .append (
                QuestionLike (user_id =user_id ,question_id =random .choice (question_ids ),value =value )
                )
            else :
                alikes .append (
                AnswerLike (user_id =user_id ,answer_id =random .choice (answer_ids ),value =value )
                )

        QuestionLike .objects .bulk_create (qlikes ,batch_size =50_000 ,ignore_conflicts =True )
        AnswerLike .objects .bulk_create (alikes ,batch_size =50_000 ,ignore_conflicts =True )

        self .stdout .write (self .style .SUCCESS ("Done."))
