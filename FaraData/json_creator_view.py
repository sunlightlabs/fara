import json
import re

from django.shortcuts import render

from FaraData.models import Recipient, Lobbyist, Client

#may not be the best way to do this but it works in Json view
def makeJson(data, name):
    list = []
    for r in data:
        if name == "name":
            item = str('{"id":"%s", "name":"%s"}'%(r.id, re.sub('"', '', str(r.name))))
        if name == "lobbyist_name":
            item = str('{"id":"%s", "name":"%s"}'%(r.id, re.sub('"', '', str(r.lobbyist_name))))
        if name == "client_name":
            item = str('{"id":"%s", "name":"%s"}'%(r.id, re.sub('"', '', str(r.client_name))))
        list.append(item)
    json = re.sub("'", '', str(list))
    return json

def recip_choice(request):
    recip_choices = makeJson(Recipient.objects.all(), 'name')
    return render(request, 'recip_choice_template.html', {'recip_choices': recip_choices},)

def lobby_choice(request):
    lobby_choices = makeJson(Lobbyist.objects.all(), 'lobbyist_name')
    return render(request, 'lobby_choice_template.html', {'lobby_choices': lobby_choices},)

def client_choice(request):
    client_choices = makeJson(Client.objects.all(), 'client_name')
    return render(request, 'client_choice_template.html', {'client_choices' : client_choices},)


#add similar for lobbyists and clients