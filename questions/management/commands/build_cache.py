import datetime 
from django.core.cache import cache 
from django.core.management.base import BaseCommand 
from django.db.models import Count 
from django.utils import timezone 

from questions.models import Answer,Question,Tag,Profile 

class Command(BaseCommand):
    def add_arguments(self,parser):
        parser.add_argument("--tags-months",type=int,default=3)
        parser.add_argument("--best-days",type=int,default=7)

    def handle(self,*args,**opts):
        now=timezone.now()
        tags_from=now-datetime.timedelta(days=30*opts["tags_months"])
        best_from=now-datetime.timedelta(days=opts["best_days"])

        tags=(
            Tag.objects.filter(questions__created_at__gte=tags_from)
            .annotate(qc=Count("questions",distinct=True))
            .order_by("-qc","name")[:10]
        )
        popular=[{"name":t.name,"url":t.get_absolute_url()} for t in tags]
        cache.set("sidebar_popular_tags",popular,timeout=None)

        top_q=Question.objects.filter(created_at__gte=best_from).order_by("-rating","-created_at").values_list("author_id",flat=True)[:50]
        top_a=Answer.objects.filter(created_at__gte=best_from).order_by("-rating","-created_at").values_list("author_id",flat=True)[:50]
        ids=list(top_q)+list(top_a)
        if ids:
            counts={}
            for uid in ids:
                counts[uid]=counts.get(uid,0)+1
            top_ids=[uid for uid,_ in sorted(counts.items(),key=lambda x:(-x[1],x[0]))[:10]]
            profiles=list(Profile.objects.select_related("user").filter(user_id__in=top_ids))
            prof_map={p.user_id:p for p in profiles}
            best=[]
            for uid in top_ids:
                p=prof_map.get(uid)
                if p:
                    best.append({"nickname":p.nickname})
            cache.set("sidebar_best_users",best,timeout=None)
        else:
            cache.set("sidebar_best_users",[],timeout=None)
