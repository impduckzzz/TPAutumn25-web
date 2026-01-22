from __future__ import annotations 

from math import ceil 

from django .contrib .auth import login as auth_login ,logout as auth_logout 
from django .contrib .auth .decorators import login_required 
from django .http import HttpResponseNotAllowed ,JsonResponse 
from django .shortcuts import get_object_or_404 ,redirect ,render
from django.template.loader import render_to_string 
from django .urls import reverse 
from django .utils .http import url_has_allowed_host_and_scheme 
from django .db .models import F 

from .forms import AnswerForm ,AskQuestionForm ,LoginForm ,ProfileEditForm ,SignupForm 
from .models import Answer ,AnswerLike ,Question ,QuestionLike ,Tag 
from .utils import paginate
from .realtime import publish_answer 


def index (request ):
    page =paginate (Question .objects .new (),request ,per_page =20 )
    q_votes =_user_question_votes (request ,page )
    return render (
    request ,
    "index.html",
    {"page_obj":page ,"section":"new","q_votes":q_votes },
    )


def hot (request ):
    page =paginate (Question .objects .hot (),request ,per_page =20 )
    q_votes =_user_question_votes (request ,page )
    return render (
    request ,
    "index.html",
    {"page_obj":page ,"section":"hot","q_votes":q_votes },
    )


def tag (request ,tag_name :str ):
    get_object_or_404 (Tag ,name =tag_name )
    page =paginate (Question .objects .by_tag (tag_name ),request ,per_page =20 )
    q_votes =_user_question_votes (request ,page )
    return render (
    request ,
    "tag.html",
    {"page_obj":page ,"tag_name":tag_name ,"q_votes":q_votes },
    )


def question_detail (request ,question_id :int ):
    question =get_object_or_404 (Question .objects .with_related (),pk =question_id )

    if request .method =="POST":
        if not request .user .is_authenticated :
            return redirect (f"{reverse('login')}?continue={request.get_full_path()}")
        form =AnswerForm (request .POST )
        if form .is_valid ():
            answer =form .save (author =request .user ,question =question )
            html =render_to_string("includes/answer_item.html",{"a":answer,"question":question,"a_votes":{}},request=request)
            publish_answer(question.id,html)


            higher =Answer .objects .filter (question =question ,rating__gt =answer .rating ).count ()
            equal_before =Answer .objects .filter (
            question =question ,rating =answer .rating ,created_at__lte =answer .created_at 
            ).count ()
            position =higher +equal_before 
            per_page =30 
            page_num =max (1 ,ceil (position /per_page ))
            return redirect (f"{question.get_absolute_url()}?page={page_num}#answer-{answer.id}")
    else :
        form =AnswerForm ()

    answers_qs =question .answers .select_related ("author","author__profile").order_by (
    "-rating","created_at"
    )
    page =paginate (answers_qs ,request ,per_page =30 )
    q_votes =_user_question_votes (request ,[question ])
    a_votes =_user_answer_votes (request ,page )
    return render (
    request ,
    "question.html",
    {
    "question":question ,
    "page_obj":page ,
    "form":form ,
    "q_votes":q_votes ,
    "a_votes":a_votes ,
    },
    )


def _user_question_votes (request ,page_or_list ):
    
    if not request .user .is_authenticated :
        return {}

    if hasattr (page_or_list ,"object_list"):
        questions =list (page_or_list .object_list )
    else :
        questions =list (page_or_list )

    if not questions :
        return {}

    likes =QuestionLike .objects .filter (user =request .user ,question__in =questions ).values (
    "question_id","value"
    )
    return {row ["question_id"]:row ["value"]for row in likes }


def _user_answer_votes (request ,page_or_list ):
    
    if not request .user .is_authenticated :
        return {}

    if hasattr (page_or_list ,"object_list"):
        answers =list (page_or_list .object_list )
    else :
        answers =list (page_or_list )

    if not answers :
        return {}

    likes =AnswerLike .objects .filter (user =request .user ,answer__in =answers ).values (
    "answer_id","value"
    )
    return {row ["answer_id"]:row ["value"]for row in likes }


def ajax_question_like (request ):
    if request .method !="POST":
        return JsonResponse ({"error":"method_not_allowed"},status =405 )
    if not request .user .is_authenticated :
        return JsonResponse ({"error":"auth_required"},status =403 )

    try :
        question_id =int (request .POST .get ("id","0"))
        value =int (request .POST .get ("value","0"))
    except ValueError :
        return JsonResponse ({"error":"bad_params"},status =400 )

    if value not in (1 ,-1 ):
        return JsonResponse ({"error":"bad_params"},status =400 )

    question =get_object_or_404 (Question ,pk =question_id )

    like =QuestionLike .objects .filter (user =request .user ,question =question ).first ()
    if like is None :
        QuestionLike .objects .create (user =request .user ,question =question ,value =value )
        question .rating =F ("rating")+value 
        question .save (update_fields =["rating"])
        question .refresh_from_db (fields =["rating"])
        current =value 
    else :
        if like .value ==value :

            like .delete ()
            question .rating =F ("rating")-value 
            question .save (update_fields =["rating"])
            question .refresh_from_db (fields =["rating"])
            current =0 
        else :

            delta =value -like .value 
            like .value =value 
            like .save (update_fields =["value"])
            question .rating =F ("rating")+delta 
            question .save (update_fields =["rating"])
            question .refresh_from_db (fields =["rating"])
            current =value 

    return JsonResponse ({"rating":question .rating ,"current":current })


def ajax_answer_like (request ):
    if request .method !="POST":
        return JsonResponse ({"error":"method_not_allowed"},status =405 )
    if not request .user .is_authenticated :
        return JsonResponse ({"error":"auth_required"},status =403 )

    try :
        answer_id =int (request .POST .get ("id","0"))
        value =int (request .POST .get ("value","0"))
    except ValueError :
        return JsonResponse ({"error":"bad_params"},status =400 )

    if value not in (1 ,-1 ):
        return JsonResponse ({"error":"bad_params"},status =400 )

    answer =get_object_or_404 (Answer ,pk =answer_id )

    like =AnswerLike .objects .filter (user =request .user ,answer =answer ).first ()
    if like is None :
        AnswerLike .objects .create (user =request .user ,answer =answer ,value =value )
        answer .rating =F ("rating")+value 
        answer .save (update_fields =["rating"])
        answer .refresh_from_db (fields =["rating"])
        current =value 
    else :
        if like .value ==value :
            like .delete ()
            answer .rating =F ("rating")-value 
            answer .save (update_fields =["rating"])
            answer .refresh_from_db (fields =["rating"])
            current =0 
        else :
            delta =value -like .value 
            like .value =value 
            like .save (update_fields =["value"])
            answer .rating =F ("rating")+delta 
            answer .save (update_fields =["rating"])
            answer .refresh_from_db (fields =["rating"])
            current =value 

    return JsonResponse ({"rating":answer .rating ,"current":current })


def ajax_mark_correct (request ):
    if request .method !="POST":
        return JsonResponse ({"error":"method_not_allowed"},status =405 )
    if not request .user .is_authenticated :
        return JsonResponse ({"error":"auth_required"},status =403 )

    try :
        question_id =int (request .POST .get ("question_id","0"))
        answer_id =int (request .POST .get ("answer_id","0"))
    except ValueError :
        return JsonResponse ({"error":"bad_params"},status =400 )

    question =get_object_or_404 (Question ,pk =question_id )
    if question .author_id !=request .user .id :
        return JsonResponse ({"error":"not_author"},status =403 )

    answer =get_object_or_404 (Answer ,pk =answer_id ,question =question )


    if answer .is_correct :
        Answer .objects .filter (pk =answer .pk ).update (is_correct =False )
        return JsonResponse ({"ok":True ,"correct_answer_id":0 })

    Answer .objects .filter (question =question ,is_correct =True ).update (is_correct =False )
    Answer .objects .filter (pk =answer .pk ).update (is_correct =True )
    return JsonResponse ({"ok":True ,"correct_answer_id":answer .pk })

def ajax_search(request ):
    if request.method!="GET":
        return JsonResponse({"error":"method_not_allowed"},status=405)
    term=(request.GET.get("q","") or "").strip()
    if len(term)<2:
        return JsonResponse({"results":[]})
    try:
        from django.contrib.postgres.search import SearchQuery,SearchRank,SearchVector
    except Exception:
        return JsonResponse({"results":[]})
    vector=SearchVector("title",weight="A")+SearchVector("text",weight="B")
    query=SearchQuery(term)
    qs=Question.objects.annotate(rank=SearchRank(vector,query)).filter(rank__gt=0.05).order_by("-rank","-created_at")[:5]
    results=[]
    for q in qs:
        results.append({"id":q.id,"title":q.title,"url":q.get_absolute_url()})
    return JsonResponse({"results":results})



@login_required 
def ask (request ):
    if request .method =="POST":
        form =AskQuestionForm (request .POST )
        if form .is_valid ():
            q =form .save (author =request .user )
            return redirect (q .get_absolute_url ())
    elif request .method =="GET":
        form =AskQuestionForm ()
    else :
        return HttpResponseNotAllowed (["GET","POST"])

    return render (request ,"ask.html",{"form":form })


def login_view (request ):
    continue_url =request .GET .get ("continue")or request .POST .get ("continue")or ""
    if request .method =="POST":
        form =LoginForm (request .POST )
        if form .is_valid ():
            auth_login (request ,form .cleaned_data ["user"])
            if continue_url and url_has_allowed_host_and_scheme (
            continue_url ,allowed_hosts ={request .get_host ()},require_https =request .is_secure ()
            ):
                return redirect (continue_url )
            return redirect ("home")
    elif request .method =="GET":
        form =LoginForm ()
    else :
        return HttpResponseNotAllowed (["GET","POST"])

    return render (request ,"login.html",{"form":form ,"continue":continue_url })


def signup_view (request ):
    if request .method =="POST":
        form =SignupForm (request .POST )
        if form .is_valid ():
            user =form .save ()
            auth_login (request ,user )
            return redirect ("home")
    elif request .method =="GET":
        form =SignupForm ()
    else :
        return HttpResponseNotAllowed (["GET","POST"])

    return render (request ,"signup.html",{"form":form })


def logout_view (request ):

    next_url =request .GET .get ("next")or request .META .get ("HTTP_REFERER")or redirect ("home").url 
    auth_logout (request )
    if next_url and url_has_allowed_host_and_scheme (
    next_url ,allowed_hosts ={request .get_host ()},require_https =request .is_secure ()
    ):
        return redirect (next_url )
    return redirect ("home")


@login_required 
def profile_edit (request ):
    if request .method =="POST":
        form =ProfileEditForm (request .user ,request .POST ,request .FILES )
        if form .is_valid ():
            form .save ()
            return redirect ("profile_edit")
    elif request .method =="GET":
        form =ProfileEditForm (request .user )
    else :
        return HttpResponseNotAllowed (["GET","POST"])

    return render (request ,"settings.html",{"form":form })
