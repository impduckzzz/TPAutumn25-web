from django.db import migrations 
from django.contrib.postgres.indexes import GinIndex 
from django.contrib.postgres.search import SearchVector 

class Migration(migrations.Migration):
    dependencies=[("questions","0001_initial")]
    operations=[
        migrations.AddIndex(
            model_name="question",
            index=GinIndex(SearchVector("title","text"),name="question_search_gin"),
        ),
    ]
