from django.urls import path
from . import views

urlpatterns = [
    path('', views.question_list, name='home'),
    path('question/<int:id>/', views.question_detail, name='question_detail'),
    path('ask/', views.ask_question, name='ask'),
    path('templates/login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
]
