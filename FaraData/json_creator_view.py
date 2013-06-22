import json

from django.http import HttpResponse
from django.shortcuts import render

from FaraData.models import Recipient, Lobbyist, Client

def makeJson(data, name):
    choice_list = []
    for r in data:
        if name == "name":
            item = {"id": r.id, "name":r.name}
        if name == "lobbyist_name":
            item = {"id": r.id, "name":r.lobbyist_name}
        if name == "client_name":
            item = {"id":r.id, "name":r.client_name}
        choice_list.append(item)
    json_choices = json.dumps(choice_list, separators=(',',':'))
    return json_choices

def recip_choice(request):
    recip_choices = makeJson(Recipient.objects.all(), 'name')
    return HttpResponse(recip_choices, mimetype="application/json")

def lobby_choice(request):
    lobby_choices = makeJson(Lobbyist.objects.all(), 'lobbyist_name')
    return HttpResponse(lobby_choices, mimetype="application/json")

def client_choice(request):
    client_choices = makeJson(Client.objects.all(), 'client_name')
    return HttpResponse(client_choices, mimetype="application/json")
