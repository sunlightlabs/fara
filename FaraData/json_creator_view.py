import json

from django.http import HttpResponse
from django.shortcuts import render

from FaraData.models import Recipient, Lobbyist, Client

def makeJson(data, name):
    choice_list = []
    for r in data:
        if name == "name":
            item = {"id": r.id, "text":r.name}
        if name == "lobbyist_name":
            item = {"id": r.id, "text":r.lobbyist_name}
        if name == "client_name":
            item = {"id":r.id, "text":r.client_name}
        choice_list.append(item)
    json_choices = json.dumps(choice_list, separators=(',',':'))
    return json_choices

def recip_choice(request):
    q =  request.GET.get('q', None)
    if q:
        recip_choices = Recipient.objects.filter(name__iregex=q)
    
    else:
        recip_choices = Recipient.objects.all()
    
    recip_choices = makeJson(recip_choices, 'name')
    return HttpResponse(recip_choices, mimetype="application/json")

def lobby_choice(request):
    q = request.GET.get('q', None)
    if q:
        lobby_choices = Lobbyist.objects.filter(lobbyist_name__iregex=q)
    
    else:
        lobby_choices = Lobbyist.objects.all()

    lobby_choices = makeJson(lobby_choices, 'lobbyist_name')
    return HttpResponse(lobby_choices, mimetype="application/json")



def client_choice(request):
    q = request.GET.get('q', None)
    if q:
        client_choices = Client.objects.filter(client_name__iregex=q)
    
    else:
        client_choices = Client.objects.all()
    
    client_choices = makeJson(client_choices, 'client_name')
    return HttpResponse(client_choices, mimetype="application/json")
