import json

from django.http import HttpResponse
from django.shortcuts import render

from FaraData.models import Recipient, Lobbyist, Client, Location, Registrant

def makeJson(data, name):
    choice_list = []
    for r in data:
        if name == "name":
            item = {"id": r.id, "text":r.name}
        if name == "lobbyist_name":
            item = {"id": r.id, "text":r.lobbyist_name}
        if name == "client_name":
            item = {"id": r.id, "text":r.client_name}
        if name == "location": 
            item = {"id": r.id, "text":r.location}
        if name == "reg_name":
            item = {"id": r.reg_id, "text":r.reg_name}
        choice_list.append(item)
    json_choices = json.dumps(choice_list, separators=(',',':'))
    return json_choices


def recip_choice(request):
    q =  request.GET.get('q', None)
    if q:
        recip_choices = Recipient.objects.filter(name__iregex=q)
    else:
        recip_choices = Recipient.objects.all()
    
    choice_list = []
    for r in recip_choices:
        name = r.name
        office = r.office_detail
        title = r.title

        if title == None or title == '':
            if office == None or office == '':
                final_name = name
            else:
                final_name = name + " (" + office + ")"
        else:
            if office == None or office == '':
                final_name = title +  " " + name
            else:
                final_name = title + " " + name + " (" + office + ")"



        item = {"id": r.id, "text": final_name}
        choice_list.append(item)
    recip_choices = json.dumps(choice_list, separators=(',',':'))

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


def location_choice(request):
    q = request.GET.get('q', None)
    if q:
        location_choices = Location.objects.filter(location__iregex=q)
    else:
        location_choices = Location.objects.all()

    location_choices = makeJson(location_choices, 'location')
    return HttpResponse(location_choices, mimetype="application/json")

def reg_choice(request):
    q = request.GET.get('q', None)
    if q:
        reg_choices = Registrant.objects.filter(reg_name__iregex=q)
    else:
        reg_choices = Registrant.objects.all()

    reg_choices = makeJson(reg_choices, 'reg_name')
    return HttpResponse(reg_choices, mimetype="application/json")


