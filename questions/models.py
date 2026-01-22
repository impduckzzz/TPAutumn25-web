from __future__ import annotations 

from django .contrib .auth .models import User
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVector 
from django .db import models 
from django .db .models import Count 
from django .urls import reverse 


class QuestionQuerySet (models .QuerySet ):
    def with_related (self )->"QuestionQuerySet":
        return (
        self .select_related ("author","author__profile")
        .prefetch_related ("tags")
        .annotate (answers_count =Count ("answers",distinct =True ))
        )

    def new (self )->"QuestionQuerySet":
        return self .with_related ().order_by ("-created_at")

    def hot (self )->"QuestionQuerySet":
        return self .with_related ().order_by ("-rating","-created_at")

    def by_tag (self ,tag_name :str )->"QuestionQuerySet":
        return self .filter (tags__name =tag_name ).hot ()


class QuestionManager (models .Manager ):
    def get_queryset (self )->QuestionQuerySet :
        return QuestionQuerySet (self .model ,using =self ._db )

    def new (self )->QuestionQuerySet :
        return self .get_queryset ().new ()

    def hot (self )->QuestionQuerySet :
        return self .get_queryset ().hot ()

    def by_tag (self ,tag_name :str )->QuestionQuerySet :
        return self .get_queryset ().by_tag (tag_name )

    def with_related (self )->QuestionQuerySet :
        return self .get_queryset ().with_related ()


class Profile (models .Model ):
    user =models .OneToOneField (User ,on_delete =models .CASCADE ,related_name ="profile")
    nickname =models .CharField (max_length =64 ,unique =True )
    avatar =models .ImageField (upload_to ="avatars/",blank =True ,null =True )

    def __str__ (self )->str :
        return self .nickname 


class Tag (models .Model ):
    name =models .CharField (max_length =64 ,unique =True ,db_index =True )

    def __str__ (self )->str :
        return self .name 

    def get_absolute_url (self )->str :
        return reverse ("tag",args =[self .name ])


class Question (models .Model ):
    title =models .CharField (max_length =255 )
    text =models .TextField ()
    author =models .ForeignKey (User ,on_delete =models .CASCADE ,related_name ="questions")
    created_at =models .DateTimeField (auto_now_add =True ,db_index =True )
    rating =models .IntegerField (default =0 ,db_index =True )
    tags =models .ManyToManyField (Tag ,related_name ="questions",blank =True )

    objects =QuestionManager ()

    class Meta:
        indexes=[GinIndex(SearchVector('title','text',config='simple'),name='question_search_gin')]

    def __str__ (self )->str :
        return self .title 

    def get_absolute_url (self )->str :
        return reverse ("question_detail",args =[self .pk ])


class Answer (models .Model ):
    question =models .ForeignKey (Question ,on_delete =models .CASCADE ,related_name ="answers")
    text =models .TextField ()
    author =models .ForeignKey (User ,on_delete =models .CASCADE ,related_name ="answers")
    created_at =models .DateTimeField (auto_now_add =True ,db_index =True )
    is_correct =models .BooleanField (default =False )
    rating =models .IntegerField (default =0 ,db_index =True )

    def __str__ (self )->str :
        return f"Answer #{self.pk}"


class QuestionLike (models .Model ):
    VALUE_CHOICES =((1 ,"+"),(-1 ,"-"))

    user =models .ForeignKey (User ,on_delete =models .CASCADE )
    question =models .ForeignKey (Question ,on_delete =models .CASCADE ,related_name ="likes")
    value =models .SmallIntegerField (choices =VALUE_CHOICES )
    created_at =models .DateTimeField (auto_now_add =True )

    class Meta :
        constraints =[
        models .UniqueConstraint (fields =["user","question"],name ="uniq_user_question_like")
        ]


class AnswerLike (models .Model ):
    VALUE_CHOICES =((1 ,"+"),(-1 ,"-"))

    user =models .ForeignKey (User ,on_delete =models .CASCADE )
    answer =models .ForeignKey (Answer ,on_delete =models .CASCADE ,related_name ="likes")
    value =models .SmallIntegerField (choices =VALUE_CHOICES )
    created_at =models .DateTimeField (auto_now_add =True )

    class Meta :
        constraints =[
        models .UniqueConstraint (fields =["user","answer"],name ="uniq_user_answer_like")
        ]
