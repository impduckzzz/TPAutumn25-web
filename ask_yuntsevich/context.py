from django.conf import settings 

def centrifugo(request):
    return {"CENTRIFUGO_WS_URL":getattr(settings,"CENTRIFUGO_WS_URL","")}
