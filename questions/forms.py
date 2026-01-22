from __future__ import annotations 

from dataclasses import dataclass 
from typing import Iterable ,List 

from django import forms 
from django .contrib .auth import authenticate 
from django .contrib .auth .models import User 
from django .core .exceptions import ValidationError 

from .models import Answer ,Profile ,Question ,Tag 


def _bootstrap (widget :forms .Widget )->forms .Widget :

    css =widget .attrs .get ("class","")
    widget .attrs ["class"]=(css +" form-control").strip ()
    return widget 


class LoginForm (forms .Form ):
    username =forms .CharField (max_length =150 ,label ="Login")
    password =forms .CharField (widget =forms .PasswordInput ,label ="Password")

    def __init__ (self ,*args ,**kwargs ):
        super ().__init__ (*args ,**kwargs )
        _bootstrap (self .fields ["username"].widget )
        _bootstrap (self .fields ["password"].widget )

    def clean (self ):
        cleaned =super ().clean ()
        username =cleaned .get ("username")
        password =cleaned .get ("password")
        if not username or not password :
            return cleaned 

        user =authenticate (username =username ,password =password )
        if user is None :
            raise ValidationError ("Sorry, wrong password!",code ="invalid_login")
        cleaned ["user"]=user 
        return cleaned 


class SignupForm (forms .Form ):
    username =forms .CharField (max_length =150 ,label ="Nick")
    email =forms .EmailField (label ="Email")
    password1 =forms .CharField (widget =forms .PasswordInput ,label ="Password")
    password2 =forms .CharField (widget =forms .PasswordInput ,label ="Repeat password")

    def __init__ (self ,*args ,**kwargs ):
        super ().__init__ (*args ,**kwargs )
        for name in ("username","email","password1","password2"):
            _bootstrap (self .fields [name ].widget )

    def clean_username (self ):
        username =self .cleaned_data ["username"].strip ()
        if User .objects .filter (username__iexact =username ).exists ():
            raise ValidationError ("This nick is already taken.",code ="username_exists")
        return username 

    def clean_email (self ):
        email =self .cleaned_data ["email"].strip ().lower ()
        if User .objects .filter (email__iexact =email ).exists ():
            raise ValidationError ("This email address already registered!",code ="email_exists")
        return email 

    def clean (self ):
        cleaned =super ().clean ()
        p1 =cleaned .get ("password1")
        p2 =cleaned .get ("password2")
        if p1 and p2 and p1 !=p2 :
            self .add_error ("password2","Passwords do not match.")
        return cleaned 

    def save (self )->User :
        username =self .cleaned_data ["username"]
        email =self .cleaned_data ["email"]
        password =self .cleaned_data ["password1"]
        user =User .objects .create_user (username =username ,email =email ,password =password )


        Profile .objects .filter (user =user ).update (nickname =username )
        return user 


class ProfileEditForm (forms .Form ):
    username =forms .CharField (max_length =150 ,label ="Nick")
    email =forms .EmailField (label ="Email")
    avatar =forms .ImageField (label ="Upload avatar",required =False )

    def __init__ (self ,user :User ,*args ,**kwargs ):
        self ._user =user 
        super ().__init__ (*args ,**kwargs )
        for name in ("username","email"):
            _bootstrap (self .fields [name ].widget )
        self .fields ["avatar"].widget .attrs ["class"]="form-control"


        self .fields ["username"].initial =user .username 
        self .fields ["email"].initial =user .email 

    def clean_username (self ):
        username =self .cleaned_data ["username"].strip ()
        qs =User .objects .filter (username__iexact =username ).exclude (pk =self ._user .pk )
        if qs .exists ():
            raise ValidationError ("This nick is already taken.",code ="username_exists")
        return username 

    def clean_email (self ):
        email =self .cleaned_data ["email"].strip ().lower ()
        qs =User .objects .filter (email__iexact =email ).exclude (pk =self ._user .pk )
        if qs .exists ():
            raise ValidationError ("This email address already registered!",code ="email_exists")
        return email 

    def save (self )->User :
        user =self ._user 
        user .username =self .cleaned_data ["username"]
        user .email =self .cleaned_data ["email"]
        user .save (update_fields =["username","email"])

        profile =user .profile 
        profile .nickname =user .username 
        if self .cleaned_data .get ("avatar")is not None :
            profile .avatar =self .cleaned_data ["avatar"]
        profile .save ()
        return user 


class AskQuestionForm (forms .Form ):
    title =forms .CharField (max_length =255 ,label ="Title")
    text =forms .CharField (widget =forms .Textarea (attrs ={"rows":8 }),label ="Text")
    tags =forms .CharField (
    required =False ,
    max_length =256 ,
    label ="Tags",
    help_text ="Comma-separated, up to 3 tags.",
    )

    def __init__ (self ,*args ,**kwargs ):
        super ().__init__ (*args ,**kwargs )
        _bootstrap (self .fields ["title"].widget )
        _bootstrap (self .fields ["tags"].widget )
        _bootstrap (self .fields ["text"].widget )

    def clean_tags (self )->List [str ]:
        raw =(self .cleaned_data .get ("tags")or "").strip ()
        if not raw :
            return []

        parts =[p .strip ()for p in raw .split (",")]
        parts =[p for p in parts if p ]

        seen =set ()
        tags :List [str ]=[]
        for p in parts :
            key =p .lower ()
            if key in seen :
                continue 
            seen .add (key )
            tags .append (p )

        if len (tags )>3 :
            raise ValidationError ("No more than 3 tags.",code ="too_many_tags")

        for t in tags :
            if len (t )>64 :
                raise ValidationError ("Tag is too long (max 64).",code ="tag_too_long")
        return tags 

    def save (self ,author :User )->Question :
        question =Question .objects .create (
        title =self .cleaned_data ["title"],
        text =self .cleaned_data ["text"],
        author =author ,
        )

        tag_names =self .cleaned_data .get ("tags")or []
        tag_objs :List [Tag ]=[]
        for name in tag_names :
            obj ,_ =Tag .objects .get_or_create (name =name )
            tag_objs .append (obj )
        if tag_objs :
            question .tags .set (tag_objs )
        return question 


class AnswerForm (forms .Form ):
    text =forms .CharField (widget =forms .Textarea (attrs ={"rows":5 }),label ="")

    def __init__ (self ,*args ,**kwargs ):
        super ().__init__ (*args ,**kwargs )
        _bootstrap (self .fields ["text"].widget )
        self .fields ["text"].widget .attrs ["placeholder"]="Enter your answer here..."

    def save (self ,author :User ,question :Question )->Answer :
        return Answer .objects .create (author =author ,question =question ,text =self .cleaned_data ["text"])
