

from django .conf import settings 
from django .db import migrations ,models 
import django .db .models .deletion 


class Migration (migrations .Migration ):

    initial =True 

    dependencies =[
    migrations .swappable_dependency (settings .AUTH_USER_MODEL ),
    ]

    operations =[
    migrations .CreateModel (
    name ="Profile",
    fields =[
    ("id",models .BigAutoField (auto_created =True ,primary_key =True ,serialize =False ,verbose_name ="ID")),
    ("nickname",models .CharField (max_length =64 ,unique =True )),
    ("avatar",models .ImageField (blank =True ,null =True ,upload_to ="avatars/")),
    (
    "user",
    models .OneToOneField (on_delete =django .db .models .deletion .CASCADE ,related_name ="profile",to =settings .AUTH_USER_MODEL ),
    ),
    ],
    ),
    migrations .CreateModel (
    name ="Tag",
    fields =[
    ("id",models .BigAutoField (auto_created =True ,primary_key =True ,serialize =False ,verbose_name ="ID")),
    ("name",models .CharField (db_index =True ,max_length =64 ,unique =True )),
    ],
    ),
    migrations .CreateModel (
    name ="Question",
    fields =[
    ("id",models .BigAutoField (auto_created =True ,primary_key =True ,serialize =False ,verbose_name ="ID")),
    ("title",models .CharField (max_length =255 )),
    ("text",models .TextField ()),
    ("created_at",models .DateTimeField (auto_now_add =True ,db_index =True )),
    ("rating",models .IntegerField (db_index =True ,default =0 )),
    (
    "author",
    models .ForeignKey (on_delete =django .db .models .deletion .CASCADE ,related_name ="questions",to =settings .AUTH_USER_MODEL ),
    ),
    ],
    ),
    migrations .CreateModel (
    name ="Answer",
    fields =[
    ("id",models .BigAutoField (auto_created =True ,primary_key =True ,serialize =False ,verbose_name ="ID")),
    ("text",models .TextField ()),
    ("created_at",models .DateTimeField (auto_now_add =True ,db_index =True )),
    ("is_correct",models .BooleanField (default =False )),
    ("rating",models .IntegerField (db_index =True ,default =0 )),
    (
    "author",
    models .ForeignKey (on_delete =django .db .models .deletion .CASCADE ,related_name ="answers",to =settings .AUTH_USER_MODEL ),
    ),
    (
    "question",
    models .ForeignKey (on_delete =django .db .models .deletion .CASCADE ,related_name ="answers",to ="questions.question"),
    ),
    ],
    ),
    migrations .CreateModel (
    name ="AnswerLike",
    fields =[
    ("id",models .BigAutoField (auto_created =True ,primary_key =True ,serialize =False ,verbose_name ="ID")),
    ("value",models .SmallIntegerField (choices =[(1 ,"+"),(-1 ,"-")])),
    ("created_at",models .DateTimeField (auto_now_add =True )),
    (
    "answer",
    models .ForeignKey (on_delete =django .db .models .deletion .CASCADE ,related_name ="likes",to ="questions.answer"),
    ),
    (
    "user",
    models .ForeignKey (on_delete =django .db .models .deletion .CASCADE ,to =settings .AUTH_USER_MODEL ),
    ),
    ],
    options ={
    "constraints":[
    models .UniqueConstraint (fields =("user","answer"),name ="uniq_user_answer_like")
    ]
    },
    ),
    migrations .CreateModel (
    name ="QuestionLike",
    fields =[
    ("id",models .BigAutoField (auto_created =True ,primary_key =True ,serialize =False ,verbose_name ="ID")),
    ("value",models .SmallIntegerField (choices =[(1 ,"+"),(-1 ,"-")])),
    ("created_at",models .DateTimeField (auto_now_add =True )),
    (
    "question",
    models .ForeignKey (on_delete =django .db .models .deletion .CASCADE ,related_name ="likes",to ="questions.question"),
    ),
    (
    "user",
    models .ForeignKey (on_delete =django .db .models .deletion .CASCADE ,to =settings .AUTH_USER_MODEL ),
    ),
    ],
    options ={
    "constraints":[
    models .UniqueConstraint (fields =("user","question"),name ="uniq_user_question_like")
    ]
    },
    ),
    migrations .AddField (
    model_name ="question",
    name ="tags",
    field =models .ManyToManyField (blank =True ,related_name ="questions",to ="questions.tag"),
    ),
    ]
