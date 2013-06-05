from django.template import Context, loader
from FaraData.models import Registrant
from django.shortcuts import render_to_response


def index(request):
    reg = Registrant.objects.all()
   
    return render_to_response('reg.html', {"reg" : reg})


