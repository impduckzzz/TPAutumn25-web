import json 
import requests 
from django.conf import settings 

def publish_answer(question_id,html):
    url=getattr(settings,"CENTRIFUGO_API_URL","")
    key=getattr(settings,"CENTRIFUGO_API_KEY","")
    if not url or not key:
        return 
    payload={"method":"publish","params":{"channel":f"question:{question_id}","data":{"html":html}}}
    headers={"Content-Type":"application/json","Authorization":f"apikey {key}"}
    try:
        requests.post(url,data=json.dumps(payload),headers=headers,timeout=1)
    except Exception:
        return
