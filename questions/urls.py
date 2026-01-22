from django .urls import path 

from .import views 

urlpatterns =[
path ("",views .index ,name ="home"),
path ("hot/",views .hot ,name ="hot"),
path ("tag/<str:tag_name>/",views .tag ,name ="tag"),
path ("question/<int:question_id>/",views .question_detail ,name ="question_detail"),
path ("ask/",views .ask ,name ="ask"),
path ("login/",views .login_view ,name ="login"),
path ("logout/",views .logout_view ,name ="logout"),
path ("signup/",views .signup_view ,name ="signup"),
path ("profile/edit/",views .profile_edit ,name ="profile_edit"),

path ("ajax/question-like/",views .ajax_question_like ,name ="ajax_question_like"),
path ("ajax/answer-like/",views .ajax_answer_like ,name ="ajax_answer_like"),
path ("ajax/mark-correct/",views .ajax_mark_correct ,name ="ajax_mark_correct"),

path ("ajax/search/",views .ajax_search ,name ="ajax_search"),

path ("settings/",views .profile_edit ,name ="settings"),
]
