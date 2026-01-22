import os 
from pathlib import Path 

BASE_DIR =Path (__file__ ).resolve ().parent .parent 

SECRET_KEY ="dev-secret-key"
DEBUG =True 
ALLOWED_HOSTS =["*"]

INSTALLED_APPS =[
"django.contrib.admin",
"django.contrib.auth",
"django.contrib.contenttypes",
"django.contrib.sessions",
"django.contrib.messages",
"django.contrib.staticfiles",
"django.contrib.postgres",
"questions.apps.QuestionsConfig",
]

MIDDLEWARE =[
"django.middleware.security.SecurityMiddleware",
"django.contrib.sessions.middleware.SessionMiddleware",
"django.middleware.common.CommonMiddleware",
"django.middleware.csrf.CsrfViewMiddleware",
"django.contrib.auth.middleware.AuthenticationMiddleware",
"django.contrib.messages.middleware.MessageMiddleware",
"django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF ="ask_yuntsevich.urls"

TEMPLATES =[
{
"BACKEND":"django.template.backends.django.DjangoTemplates",
"DIRS":[BASE_DIR /"templates"],
"APP_DIRS":True ,
"OPTIONS":{
"context_processors":[
"django.template.context_processors.debug",
"django.template.context_processors.request",
"django.contrib.auth.context_processors.auth",
"django.contrib.messages.context_processors.messages",
"ask_yuntsevich.context.centrifugo",
],
},
}
]

WSGI_APPLICATION ="ask_yuntsevich.wsgi.application"

DATABASES ={
"default":{
"ENGINE":"django.db.backends.postgresql",
"NAME":os .environ .get ("POSTGRES_DB","ask_yuntsevich"),
"USER":os .environ .get ("POSTGRES_USER","ask_yuntsevich"),
"PASSWORD":os .environ .get ("POSTGRES_PASSWORD","ask_yuntsevich"),
"HOST":os .environ .get ("POSTGRES_HOST","127.0.0.1"),
"PORT":os .environ .get ("POSTGRES_PORT","5432"),
}
}

AUTH_PASSWORD_VALIDATORS =[]

LANGUAGE_CODE ="ru-ru"
TIME_ZONE ="Europe/Moscow"
USE_I18N =True 
USE_TZ =True 

STATIC_URL ="/static/"
STATICFILES_DIRS =[BASE_DIR /"static"]
MEDIA_URL ="/uploads/"
MEDIA_ROOT =BASE_DIR /"uploads"

DEFAULT_AUTO_FIELD ="django.db.models.BigAutoField"

LOGIN_URL ="login"

CACHES ={
"default":{
"BACKEND":"django.core.cache.backends.locmem.LocMemCache",
"LOCATION":"ask_yuntsevich",
}
}

if os.getenv("MEMCACHED_HOST"):
    CACHES={
    "default":{
    "BACKEND":"django.core.cache.backends.memcached.PyMemcacheCache",
    "LOCATION":f"{os.getenv('MEMCACHED_HOST')}:{os.getenv('MEMCACHED_PORT','11211')}",
    }
    }

CENTRIFUGO_API_URL =os.getenv("CENTRIFUGO_API_URL","http://127.0.0.1:8001/api")
CENTRIFUGO_API_KEY =os.getenv("CENTRIFUGO_API_KEY","")
CENTRIFUGO_WS_URL =os.getenv("CENTRIFUGO_WS_URL","ws://127.0.0.1:8001/connection/websocket")
