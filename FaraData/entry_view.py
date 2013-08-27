import re
import json
from datetime import datetime, date

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from FaraData.models import * #LobbyistForm, ClientForm, RegForm, RecipientForm, ContactForm, PaymentForm, ContributionForm, Disbursement, DisbursementForm
from fara_feed.models import Document

#change GET to POST, but GET is better for debugging

# Section for functions that create variables for the templates 

# this gets the info about the form
def doc_id(form_id):
    doc = Document.objects.get(id = form_id)
    url = doc.url
    reg_id = doc.reg_id 
    # this enters the system with the wrong month so correct manually for now
    s_date = doc.stamp_date
    return (url, reg_id, s_date)
      
#looks up registrant info already in the system    
def reg_info(id):
    try:  
        reg_object = Registrant.objects.get(reg_id = id)   
        return reg_object
    except:
        return None
        #there may be a better way to do this but it keeps the page from crashing if there isn't anything in the system

#finds disbursements attached to this form 
def dis_info(url):
    dis_objects = Disbursement.objects.filter(link = url)
    dis_list = []
    for dis in dis_objects: 
        dis_list.append([dis.client, dis.amount, dis.date, dis.id]) 
    return dis_list 

#finds payments attached to this form 
def pay_info(url):
    pay_objects = Payment.objects.filter(link = url) 
    pay_list = []
    for pay in pay_objects: 
        pay_list.append([pay.client, pay.amount, pay.fee, pay.date, pay.id])
    return pay_list

#finds contacts attached to this form 
def contact_info(url):
    contact_objects = Contact.objects.filter(link = url)
    contact_list = []
    for con in contact_objects:
        con_id = int(con.id)
        for recipient in con.recipient.all():
            contact_list.append([recipient.title, recipient.name, recipient.agency, con.date, con_id ])
    return (contact_list)

#finds contributions attached to this form        
def cont_info(url):
    cont_objects = Contribution.objects.filter(link = url) 
    cont_list = []
    for cont in cont_objects: 
        cont_list.append([cont.lobbyist, cont.amount, cont.recipient, cont.date, cont.id])
    return cont_list
               
#finds gifts attached to the form
def gift_info(url):
    gift_objects = Gift.objects.filter(link = url) 
    gift_list = []
    for g in gift_objects:
        gift = [g.description, g.date]
        for g in g.client.all():
            gift.append(g.client_name)
        gift_list.append(gift)
    return (gift_list)

#finds meta data attached to form 
def meta_info(url):
    try:
        m = MetaData.objects.get(link=url)
        meta_list = [ m.reviewed, m.processed, m.upload_date, m.is_amendment, m.notes, m.end_date] 
    except:
        metadata= MetaData(
            link = url,
            upload_date = date.today(),
            reviewed = False,
            processed = False,
        )
        metadata.save()
        meta_list = [ False, False, date.today(), False, '']
    return meta_list 

def oneclient(reg_object):
    try:
        clients = reg_object.clients.all()
        if len(reg_object.clients.all()) == 1:
            one_client = True
        else:
            one_client = False
    except:
        one_client = False
    return one_client

# Section for rendering pages

#all in one supplemental data entry form- good for amendments
def return_big_form(request, form_id):
        url, reg_id, s_date = doc_id(form_id)
        #forms
        client_form = ClientForm()
        reg_form = RegForm()
        recipient_form = RecipientForm()
        #options for the forms
        all_clients = Client.objects.all()
        all_lobbyists = Lobbyist.objects.all()
        all_recipients = Recipient.objects.all()
        #for displaying information already in the system
        reg_object = reg_info(reg_id)
        one_client = oneclient(reg_object)
        contact_list = contact_info(url)
        dis_list = dis_info(url)
        pay_list = pay_info(url)
        cont_list = cont_info(url)
        gift_list = gift_info(url)
        meta_list = meta_info(url)


        return render(request, 'FaraData/entry_form.html',{
            'recipient_form': recipient_form,
            #'lobby_form': lobby_form,
            'client_form': client_form,
            'reg_form': reg_form,
            #options for forms
            'all_clients': all_clients,
            'all_lobbyists': all_lobbyists,
            'all_recipients': all_recipients,
            'url': url, 
            'reg_object': reg_object,
            'contact_list': contact_list,
            'dis_list' : dis_list,
            'gift_list': gift_list,
            'pay_list' : pay_list,
            'cont_list' : cont_list,
            'meta_list' : meta_list,
            'reg_id' : reg_id,
            'form_id' : form_id,
            's_date' : s_date,
            'one_client' : one_client,
        })

@login_required(login_url='/admin')
def index(request, form_id):
    return return_big_form(request, form_id)

#multi-step supplemental form
@login_required(login_url='/admin')
def supplemental_base(request, form_id):
    return render(request, 'FaraData/supplemental_base.html', {'form_id': form_id})   

@login_required(login_url='/admin')
def supplemental_first(request, form_id):
    url, reg_id, s_date = doc_id(form_id)
    reg_object = reg_info(reg_id)
    all_clients = Client.objects.all()
    client_form = ClientForm()

    return render(request, 'FaraData/supplemental_first.html',{
        'reg_id' : reg_id,
        'reg_object': reg_object,
        'url': url,
        'all_clients': all_clients,
        'client_form': client_form,
        'form_id': form_id,
        's_date': s_date,
    })

@login_required(login_url='/admin')
def supplemental_contact(request, form_id):
    url, reg_id, s_date = doc_id(form_id)
    reg_object = reg_info(reg_id)
    contact_list = contact_info(url)
    client_form = ClientForm()
    recipient_form = RecipientForm()
    all_recipients = Recipient.objects.all()
    all_lobbyists = Lobbyist.objects.all()
    one_client = oneclient(reg_object)

    return render(request, 'FaraData/supplemental_contact.html',{
        'reg_id' : reg_id,
        'reg_object': reg_object,
        'one_client': one_client,
        'url': url,
        'client_form': client_form,
        'form_id': form_id,
        'recipient_form': recipient_form,
        'all_recipients': all_recipients,
        'contact_list': contact_list,
        'all_lobbyists': all_lobbyists,
    })

@login_required(login_url='/admin')
def supplemental_payment(request, form_id):
    url, reg_id, s_date = doc_id(form_id)
    pay_list = pay_info(url)
    reg_object = reg_info(reg_id)
    one_client = oneclient(reg_object)

    return render(request, 'FaraData/supplemental_payment.html',{
    'reg_id' : reg_id,
    'url': url,
    'pay_list' : pay_list,
    'reg_object': reg_object,
    'form_id': form_id,
    'one_client': one_client,
    })

@login_required(login_url='/admin')
def supplemental_gift(request, form_id):
    url, reg_id, s_date = doc_id(form_id)
    gift_list = gift_info(url)
    reg_object = reg_info(reg_id)
    recipient_form= RecipientForm()

    return render(request, 'FaraData/supplemental_gift.html',{
    'reg_id' : reg_id,
    'url': url,
    'form_id': form_id,
    'reg_object': reg_object,
    'gift_list': gift_list,
    'recipient_form': recipient_form,
    })

@login_required(login_url='/admin')
def supplemental_disbursement(request, form_id):
    url, reg_id, s_date = doc_id(form_id)
    reg_object = reg_info(reg_id)
    dis_list = dis_info(url)
    one_client = oneclient(reg_object)

    return render(request, 'FaraData/supplemental_disbursement.html',{
    'reg_id' : reg_id,
    'url': url,
    'form_id': form_id,
    'reg_object': reg_object,
    'dis_list' : dis_list,
    'one_client': one_client,
    })

@login_required(login_url='/admin')
def supplemental_contribution(request, form_id):
    url, reg_id, s_date = doc_id(form_id)
    reg_object = reg_info(reg_id)
    cont_list = cont_info(url)
    all_recipients = Recipient.objects.all()
    recipient_form = RecipientForm()

    return render(request, 'FaraData/supplemental_contribution.html',{
    'reg_id': reg_id,
    'url': url,
    'form_id': form_id,
    'reg_object': reg_object,
    'cont_list': cont_list,
    'all_recipients': all_recipients,
    'recipient_form': recipient_form,
    })

@login_required(login_url='/admin')
def supplemental_last(request, form_id):
    url, reg_id, s_date= doc_id(form_id)
    meta_list = meta_info(url)

    return render(request, 'FaraData/supplemental_last.html',{
    'reg_id' : reg_id,
    'url': url,
    'form_id': form_id,
    'meta_list': meta_list,
    })

# segmented registration form
@login_required(login_url='/admin')
def registration_base(request, form_id):
    return render(request, 'FaraData/registration_base.html', {'form_id': form_id})   

@login_required(login_url='/admin')
def registration_first(request, form_id):
    url, reg_id, s_date = doc_id(form_id)
    reg_object = reg_info(reg_id)
    all_clients = Client.objects.all()
    client_form = ClientForm()

    return render(request, 'FaraData/registration_first.html',{
        'reg_id' : reg_id,
        'reg_object': reg_object,
        'url': url,
        'all_clients': all_clients,
        'client_form': client_form,
        'form_id': form_id,
        's_date': s_date,
    })

@login_required(login_url='/admin')
def registration_contact(request, form_id):
    url, reg_id, s_date = doc_id(form_id)
    reg_object = reg_info(reg_id)
    contact_list = contact_info(url)
    client_form = ClientForm()
    recipient_form = RecipientForm()
    all_recipients = Recipient.objects.all()
    one_client = oneclient(reg_object)

    return render(request, 'FaraData/registration_contact.html',{
        'reg_id' : reg_id,
        'reg_object': reg_object,
        'url': url,
        'client_form': client_form,
        'form_id': form_id,
        'recipient_form': recipient_form,
        'all_recipients': all_recipients,
        'contact_list': contact_list,
        'one_client': one_client,
    })

@login_required(login_url='/admin')
def registration_payment(request, form_id):
    url, reg_id, s_date = doc_id(form_id)
    pay_list = pay_info(url)
    reg_object = reg_info(reg_id)
    one_client = oneclient(reg_object)

    return render(request, 'FaraData/registration_payment.html',{
    'reg_id' : reg_id,
    'url': url,
    'pay_list' : pay_list,
    'reg_object': reg_object,
    'form_id': form_id,
    'one_client': one_client,
    })

@login_required(login_url='/admin')
def registration_gift(request, form_id):
    url, reg_id, s_date = doc_id(form_id)
    gift_list = gift_info(url)
    recipient_form = RecipientForm()
    reg_object = reg_info(reg_id)

    return render(request, 'FaraData/registration_gift.html',{
    'reg_id' : reg_id,
    'url': url,
    'form_id': form_id,
    'gift_list': gift_list,
    'recipient_form': recipient_form,
    'reg_object': reg_object,
    })

@login_required(login_url='/admin')
def registration_disbursement(request, form_id):
    url, reg_id, s_date = doc_id(form_id)
    reg_object = reg_info(reg_id)
    dis_list = dis_info(url)
    one_client = oneclient(reg_object)

    return render(request, 'FaraData/registration_disbursement.html',{
    'reg_id' : reg_id,
    'url': url,
    'form_id': form_id,
    'reg_object': reg_object,
    'dis_list' : dis_list,
    'one_client': one_client,
    })

@login_required(login_url='/admin')
def registration_contribution(request, form_id):
    url, reg_id, s_date = doc_id(form_id)
    reg_object = reg_info(reg_id)
    cont_list = cont_info(url)
    all_recipients = Recipient.objects.all()
    recipient_form = RecipientForm()

    return render(request, 'FaraData/registration_contribution.html',{
    'reg_id': reg_id,
    'url': url,
    'form_id': form_id,
    'reg_object': reg_object,
    'cont_list': cont_list,
    'all_recipients': all_recipients,
    'recipient_form': recipient_form,
    })

@login_required(login_url='/admin')
def registration_last(request, form_id):
    url, reg_id, s_date = doc_id(form_id)
    meta_list = meta_info(url)

    return render(request, 'FaraData/registration_last.html',{
    'reg_id' : reg_id,
    'url': url,
    'form_id': form_id,
    'meta_list': meta_list,
    })

@login_required(login_url='/admin')
def enter_AB(request, form_id):
    url, reg_id, s_date = doc_id(form_id)
    reg_object = reg_info(reg_id)
    all_clients = Client.objects.all()
    client_form = ClientForm()
    meta_list = meta_info(url)
    one_client = oneclient(reg_object)

    return render(request, 'FaraData/enter_AB.html',{
        'reg_id' : reg_id,
        'reg_object': reg_object,
        'url': url,
        'all_clients': all_clients,
        'client_form': client_form,
        'form_id': form_id,
        'meta_list': meta_list,
        's_date': s_date,
        'one_client' : one_client,
    })

# easy fix forms
@login_required(login_url='/admin')
def fix_contact(request, contact_id): 
    contact =  Contact.objects.get(id=contact_id)
    reg_object = reg_info(contact.registrant.reg_id)
    url = contact.link
    lobbyists = reg_object.lobbyists.all()
    current_lobby = contact.lobbyist.all()
    recipients = contact.recipient.all()
    date = contact.date.strftime('%m/%d/%Y')

    return render(request, 'FaraData/fix_contact.html',{
        'contact': contact,
        'reg_object': reg_object,
        'url': url,
        'lobbyists': lobbyists,
        'recipients': recipients,
        'current_lobby': current_lobby,
        'date': date,
    })

@login_required(login_url='/admin')
def fix_payment(request, payment_id):
    payment = Payment.objects.get(id=payment_id)
    reg_object = reg_info(payment.registrant.reg_id)
    url = payment.link
    date = payment.date.strftime('%m/%d/%Y')

    return render(request, 'FaraData/fix_payment.html',{
        'payment': payment,
        'reg_object': reg_object,
        'url': url,
        'date': date,
        })

@login_required(login_url='/admin')
def fix_disbursement(request, dis_id):
    disbursement = Disbursement.objects.get(id=dis_id)
    reg_object = reg_info(disbursement.registrant.reg_id)
    url = disbursement.link
    date = disbursement.date.strftime('%m/%d/%Y')

    return render(request, 'FaraData/fix_disbursement.html',{
        'disbursement': disbursement,
        'reg_object': reg_object,
        'url': url,
        'date': date,
        })

@login_required(login_url='/admin')
def fix_contribution(request, cont_id):
    contribution = Contribution.objects.get(id=cont_id)
    reg_object = reg_info(contribution.registrant.reg_id)
    url = contribution.link
    date = contribution.date.strftime('%m/%d/%Y')

    return render(request, 'FaraData/fix_contribution.html',{
        'contribution': contribution,
        'reg_object': reg_object,
        'url': url,
        'date': date,
        })

# Section for functions that process forms

#data cleaning
def cleantext(text):
    text = re.sub(' +',' ', text)
    text = re.sub('\\r|\\n','', text)
    return text

def cleanmoney(money):
    money = money.strip()
    money = money.replace('$', '').replace(',', '')
    return money

def cleandate(date):
        try:
            date_obj = datetime.strptime(request.GET['date'], "%m/%d/%Y")
            if date_obj > datetime.now():
                date_error = json.dumps({'error': 'date in the future'}, separators=(',',':'))
                return HttpResponse(date_error, mimetype="application/json")
            return date_obj
            
        except:
            date_error = json.dumps({'error': 'Incorrect date format'}, separators=(',',':'))
            return HttpResponse(date_error, mimetype="application/json")


#corrects stamp date
@login_required(login_url='/admin')
def stamp_date(request):
    if request.method == 'GET':
        try:
            s_date = datetime.strptime(request.GET['stamp_date'], "%m/%d/%Y")
            date = s_date.strftime("%B %d, %Y")
        except:
            date_error = json.dumps({'error': 'Incorrect date format'}, separators=(',',':'))
            return HttpResponse(date_error, mimetype="application/json")

        form_id = request.GET['form_id']
        document = Document.objects.get(id = form_id)
        stamp = Document(id = document.id,
                        url = document.url,
                        reg_id = document.reg_id,
                        doc_type = document.doc_type,
                        stamp_date = s_date,
        )
        if s_date > datetime.now():
            date_error = json.dumps({'error': 'date in the future'}, separators=(',',':'))
            return HttpResponse(date_error, mimetype="application/json")

        else:    
            stamp.save()
            stampinfo = {'id': form_id, 'date': date}
            stampinfo = json.dumps(stampinfo , separators=(',',':'))
            return HttpResponse(stampinfo, mimetype="application/json")   

    else:
        error = json.dumps({'error': 'failed'} , separators=(',',':'))
        return HttpResponse(error, mimetype="application/json")
  
#creates a new recipient
@login_required(login_url='/admin')
def recipient(request):
    if request.method == 'GET':
        form = RecipientForm(request.GET)
        if form.is_valid():
            recipient = Recipient(crp_id = form.cleaned_data['crp_id'],
                                agency = form.cleaned_data['agency'],
                                office_detail = form.cleaned_data['office_detail'],
                                name  = form.cleaned_data['name'],
                                title = form.cleaned_data['title'], 
            )
            if form.cleaned_data['state_local'] == True:
                recipient.state_local = True

            recipient.save()
            recip_choice = json.dumps({'name': recipient.name}, separators=(',',':'))        
            return HttpResponse(recip_choice, mimetype="application/json")
            
        else:
            return HttpResponse(request, {'error': 'failed'})

            
# creates a new lobbyist and adds it to Registrant  
@login_required(login_url='/admin')       
def lobbyist(request):
    if request.method == 'GET':
        lobbyist_name = request.GET['lobbyist_name'], 
        PAC_name = request.GET['PAC_name'], 

        for p in PAC_name:
            pac_size = len(p)
            
        for l in lobbyist_name:
            lobby_size = len (l)
        # wrapped error messages in list so they work the same as a successful variable in the JS
        if pac_size == 0 and lobby_size == 0:
            error = json.dumps([{'error': "must have lobbyist name or PAC name"}], separators=(',',':')) 
            print "too little"
            return HttpResponse(error, mimetype="application/json")
        
        if pac_size > 1 and lobby_size > 1:
            error = json.dumps([{'error': "Is this a lobbyist or a PAC? Only fill out the name in the appropriate field"}], separators=(',',':')) 
            print "too much"
            return HttpResponse(error, mimetype="application/json")
        
        reg_id = request.GET['reg_id']
        lobby = Lobbyist(lobbyist_name = request.GET['lobbyist_name'], 
                        PAC_name = request.GET['PAC_name'], 
                        lobby_id = request.GET['lobby_id'],
        )
        lobby.save()
        # adds to registrant 
        lobby_obj = Lobbyist.objects.get(id = lobby.id)
        reg_id = request.GET['reg_id']
        registrant = Registrant.objects.get(reg_id = reg_id)
        registrant.lobbyists.add(lobby_obj)
        # returns lobbyist info to add to other fields with jQuery
        name = lobby_obj.lobbyist_name + lobby_obj.PAC_name
        lobbyist_choice = [{'name': name,'id': lobby_obj.id,}]
        lobbyist_choice = json.dumps(lobbyist_choice, separators=(',',':'))        
        return HttpResponse(lobbyist_choice, mimetype="application/json")
        
    else:
        HttpResponse(request, {'error': 'failed'})

# assigns a lobbyist or lobbyists to a reg. all_lobbyists
@login_required(login_url='/admin')
def reg_lobbyist(request):
    if request.method == 'GET': 
        reg_id = (request.GET['reg_id'])
        registrant = Registrant.objects.get(reg_id=reg_id) 
        lobby_ids = request.GET.get('lobbyists')
        lobbyists = lobby_ids.split(',')
        lobby_choice = []
        
        for l_id in lobbyists:
            lobbyist = Lobbyist.objects.get(id=l_id)
            if lobbyist not in registrant.lobbyists.all():
                registrant.lobbyists.add(lobbyist)
                l = {"name" : lobbyist.lobbyist_name, "id": lobbyist.id}
                lobby_choice.append(l)

        if len(l_id) >= 1:    
            lobby_choice =  json.dumps(lobby_choice, separators=(',',':')) 
            return HttpResponse(lobby_choice, mimetype="application/json") 
        else:
            error = json.dumps({'error': "no lobbyists added"}, separators=(',',':')) 
            return HttpResponse(error, mimetype="application/json")

    else:
        error = json.dumps({'error': "failed"}, separators=(',',':')) 
        return HttpResponse(error, mimetype="application/json")

#creates a new client and adds it to the registrant 
@login_required(login_url='/admin')
def client(request):
    if request.method == 'GET': 
        # this returns a tuple

        try:
            location = Location.objects.get(id=int(request.GET['location']))
        except:
            error = json.dumps({'error': "Please add location"}, separators=(',',':')) 
            return HttpResponse(error, mimetype="application/json")

        if request.GET['client_name'] == '' or request.GET['client_name'] == None:
            error = json.dumps({'error': "Please add Client Name"}, separators=(',',':')) 
            return HttpResponse(error, mimetype="application/json")

        client = Client(client_name = request.GET['client_name'], 
                        location = location,
                        address1 = request.GET['address1'],
                        city = request.GET['city'],
                        state = request.GET['state'],
                        zip_code = request.GET['zip_code'],
        )
        if Client.objects.filter(client_name = client.client_name).exists():
            error = json.dumps({'error': "name in system"}, separators=(',',':')) 
            return HttpResponse(error, mimetype="application/json")
            
        else:
            client.save()
            registrant = Registrant.objects.get(reg_id=int(request.GET['reg_id']))

            if client not in registrant.clients.all():
                registrant.clients.add(client)
                print "added"

            client_choice = [{'name': client.client_name,'id': client.id,}]
            client_choice = json.dumps(client_choice, separators=(',',':')) 
                
            return HttpResponse(client_choice, mimetype="application/json")  
     
    else:
        HttpResponse(request, {'error': 'failed'})

@login_required(login_url='/admin')
def client_info(request):
    if request.method == 'GET': 
        try:
            client_id = int(request.GET['client'])
            client = Client.objects.get(id = client_id)
            
            # these are on 2 different form that usually come in together but I don't want them to overwrite the older entry when they come in separately 
            client_type = request.GET['client_type']
            if client_type != None and client_type != '' and client_type != "None":
                client.client_type = client_type
            
            description = request.GET['description']
            if description != None and description != '' and description != "None":
                client.description = description
            
            client.save()
            
            client_info = json.dumps({'client_id': client_id, 'client_type': request.GET['client_type'], 'description': request.GET['description']}, separators=(',',':'))
            return HttpResponse(client_info, mimetype="application/json")
   
        except:
            if request.GET['client'] == None or request.GET['client'] == '' or request.GET['client'] == "None":
                error = json.dumps({'error': 'Please select a client.'} , separators=(',',':'))
                return HttpResponse(error, mimetype="application/json")
            else:
                error = json.dumps({'error': 'failed'} , separators=(',',':'))
                return HttpResponse(error, mimetype="application/json")

@login_required(login_url='/admin')
def location(request):
    if request.method == 'GET': 
        location = Location(location = request.GET['location'],
                            country_grouping = request.GET['country'],
                            region = request.GET['region'],
        )
        location.save()
        location_info = json.dumps({'location': location.location, 'country': location.country_grouping, 'region': location.region} , separators=(',',':'))
        return HttpResponse(location_info, mimetype="application/json")

    else:
        error = json.dumps({'error': 'failed'} , separators=(',',':'))
        return HttpResponse(error, mimetype="application/json")


#creates a new registrant
@login_required(login_url='/admin') 
def registrant(request):
    if request.method == 'GET': # If the form has been submitted...
        form = RegForm(request.GET) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            registrant = Registrant(reg_id = form.cleaned_data['reg_id'],
                            reg_name = form.cleaned_data['reg_name'],
                            address = form.cleaned_data['address'],
                            city = form.cleaned_data['city'],
                            state = form.cleaned_data['state'],
                            zip = form.cleaned_data['zip'],
                            country = form.cleaned_data['country'],
                            #description = form.cleaned_data['description'],
            )
            registrant.save()
            reg_info = json.dumps({'reg_id': registrant.reg_id, 'reg_name': registrant.reg_name} , separators=(',',':'))
            return HttpResponse(reg_info, mimetype="application/json")

        else:
            error = json.dumps({'error': 'failed'} , separators=(',',':'))
            return HttpResponse(error, mimetype="application/json")

@login_required(login_url='/admin')
def new_registrant(request):
    if request.method == 'GET':
        registrant = Registrant(reg_id = request.GET['reg_id'],
                            reg_name = request.GET['reg_name'],
                            address = request.GET['address'],
                            city = request.GET['city'],
                            state = request.GET['state'],
                            zip_code = request.GET['zip'],
                            country = request.GET['country'],
        )
        registrant.save()
        reginfo = {'id': registrant.reg_id, 'name': registrant.reg_name}
        reginfo = json.dumps(reginfo , separators=(',',':'))
        return HttpResponse(reginfo, mimetype="application/json")
        
    else:
        error = json.dumps({'error': 'failed'} , separators=(',',':'))
        return HttpResponse(error, mimetype="application/json") 

                  
#adds existing client to registrant 
@login_required(login_url='/admin')
def reg_client(request):
    if request.method == 'GET': 
        reg_id = request.GET['reg_id'] 

        clients = request.GET['clients']   
        if clients == '':
            error = json.dumps({'error': 'Please select a client'} , separators=(',',':'))
            return HttpResponse(error, mimetype="application/json")
        clients = clients.split(',')

        registrant = Registrant.objects.get(reg_id=reg_id)
        client_choices = []

        for c_id in clients:
            client = Client.objects.get(id=c_id)

            if client not in registrant.clients.all():
                registrant.clients.add(client)
                client_choices.append({
                            'name': client.client_name,
                            'id': client.id,
                })

            if client in registrant.terminated_clients.all():
                registrant.terminated_clients.remove(client)
            

        client_choices = json.dumps(client_choices, separators=(',',':'))
        return HttpResponse(client_choices, mimetype="application/json") 
         
    else:
        error = json.dumps({'error': 'failed'}, separators=(',',':'))
        return HttpResponse(error, mimetype="application/json")


#adds client as terminated in registrant 
@login_required(login_url='/admin')
def terminated(request):
    if request.method == 'GET': # If the form has been submitted...
        reg_id = request.GET['reg_id'] # A form bound to the POST data
        clients = request.GET.getlist('clients')
        terminateinfo = []
        registrant = Registrant.objects.get(reg_id=reg_id)
        
        for c_id in clients:
            client = Client.objects.get(id=c_id)
            terminateinfo.append({"id":client.id, "name":client.client_name})
            
            if client not in registrant.terminated_clients.all():
                registrant.terminated_clients.add(client)
                
            if client in registrant.clients.all():
                registrant.clients.remove(client)

        terminateinfo = json.dumps(terminateinfo , separators=(',',':'))
        return HttpResponse(terminateinfo, mimetype="application/json")           
         
    else:
        error = json.dumps({'error': 'failed'} , separators=(',',':'))
        return HttpResponse(error, mimetype="application/json")


#creates contact
## fix contacts for no lobbyists
@login_required(login_url='/admin')
def contact(request):
    if request.method == 'GET':
        
        lobbyists_ids = request.GET.getlist('lobbyist')
        if not lobbyists_ids:
            lobbyists_ids = [request.GET.get('lobbyists'),]

        client = request.GET['client']
        if client == None:
            error = json.dumps({'error': 'Please select a client.'} , separators=(',',':'))
            return HttpResponse(error, mimetype="application/json")
        client = Client.objects.get(id=int(request.GET['client']))

        reg_id = Registrant.objects.get(reg_id=int(request.GET['reg_id']))
        
        date_obj = datetime.strptime(request.GET['date'], "%m/%d/%Y")
        if date_obj > datetime.now():
            date_error = json.dumps({'error': 'date in the future'}, separators=(',',':'))
            return HttpResponse(date_error, mimetype="application/json")

        lobbyists = Lobbyist.objects.filter(id__in=lobbyists_ids)
        description = cleantext(request.GET['description'])
        
        contact = Contact(registrant = reg_id,
                            contact_type = request.GET['contact_type'],
                            description = description,
                            date = date_obj,
                            link = request.GET['link'],
                            client = client,
        )
        contact.save()

        # this formats the results from the multiple select 
        recipient_ids = request.GET.get('recipient')
        recipients = recipient_ids.split(',')
        # names is formating for adding to the list in the form
        names = ''
        for r in recipients:
            recip = Recipient.objects.get(id=r)
            if recip not in contact.recipient.all():
                contact.recipient.add(recip)
                if recip.title != None and len(recip.title) > 1:
                    names = names + recip.title + ' ' + recip.name
                else:
                    names = names + recip.name
                
                if recip.agency != None and len(recip.agency) > 1:
                    names = names + ' (' + recip.agency + '), ' 
                elif recip.office_detail != None and len(recip.office_detail) > 1: 
                    names = names + ' (' +  recip.office_detail + '), ' 
                else:
                    names = names + ', '
        
        for l in lobbyists:
            if l != None and l != '' and l not in contact.lobbyist.all():
                contact.lobbyist.add(l)
        
        try:
            clear = request.GET['do_not_clear']
        except:
            clear = "off"


        date = contact.date.strftime("%B %d, %Y")
        contactinfo = {'date': date, 
                        'name': str(names), 
                        'do_not_clear': clear,
                        'contact_id': contact.id,
        }
        contactinfo = json.dumps(contactinfo , separators=(',',':'))
        return HttpResponse(contactinfo, mimetype="application/json")

     
    else:
        error = json.dumps({'error': 'failed'} , separators=(',',':'))
        return HttpResponse(error, mimetype="application/json")  
        
        
#creates payment
@login_required(login_url='/admin')
def payment(request):
    if request.method == 'GET':
        client = request.GET['client']
        if client == "None":
            error = json.dumps({'error': 'Please select a client.'} , separators=(',',':'))
            return HttpResponse(error, mimetype="application/json")
        client = Client.objects.get(id=int(client))
        
        reg_id = Registrant.objects.get(reg_id=int(request.GET['reg_id']) )
        
        try:
            date_obj = datetime.strptime(request.GET['date'], "%m/%d/%Y")
        except:
            error = json.dumps({'error': 'Invalid date format'} , separators=(',',':'))
            return HttpResponse(error, mimetype="application/json")
        
        if date_obj > datetime.now():
            date_error = json.dumps({'error': 'date in the future'}, separators=(',',':'))
            return HttpResponse(date_error, mimetype="application/json")

        if request.method == 'GET' and 'fee' in request.GET:
            fee = True
        else:
            fee = False

        purpose = cleantext(request.GET['purpose'])
        amount = cleanmoney(request.GET['amount'])
        
        payment = Payment(client = client,
                            registrant = reg_id,
                            fee = fee,
                            amount = amount,
                            purpose = purpose,
                            date = date_obj,
                            link = request.GET['link'],
        )
        payment.save()

        subcontractor_id = request.GET['subcontractor']
        if subcontractor_id != '' and subcontractor_id != None:
            subcontractor = Registrant.objects.get(reg_id = subcontractor_id )
            payment.subcontractor = subcontractor
            payment.save()

        try:
            clear = request.GET['do_not_clear']
        except:
            clear = "off"

        # return info to update the entry form
        payinfo = {"amount": payment.amount, 
                    "fee": payment.fee, 
                    "date": payment.date.strftime("%B %d, %Y"), 
                    "client": str(payment.client),
                    "pay_id": payment.id,
                    "do_not_clear": clear,
        }
        payinfo = json.dumps(payinfo , separators=(',',':'))
        return HttpResponse(payinfo, mimetype="application/json")
        
    else:
        error = json.dumps({'error': 'failed'} , separators=(',',':'))
        return HttpResponse(error, mimetype="application/json")  


#creates contributions
@login_required(login_url='/admin')
def contribution(request):
    if request.method == 'GET':
        try:
            date_obj = datetime.strptime(request.GET['date'], "%m/%d/%Y")
        except:
            error = json.dumps({'error': 'Incorrect date format'} , separators=(',',':'))
            return HttpResponse(error, mimetype="application/json")

        if date_obj > datetime.now():
            date_error = json.dumps({'error': 'date in the future'}, separators=(',',':'))
            return HttpResponse(date_error, mimetype="application/json")

        registrant = Registrant.objects.get(reg_id=int(request.GET['registrant']))
        recipient = Recipient.objects.get(id=int(request.GET['recipient']))
        
        amount = cleanmoney(request.GET['amount'])
        
        lobby = request.GET['lobbyist']
        if lobby == None or lobby == '':       
            contribution = Contribution(amount = amount, 
                                        date = date_obj, 
                                        link = request.GET['link'],
                                        registrant = registrant,
                                        recipient = recipient,
            ) 
            contribution.save()
            lobbyist = None
            
        else:
            lobby = Lobbyist.objects.get(id=int(request.GET['lobbyist'])) 
            contribution = Contribution(amount = amount, 
                                        date = date_obj, 
                                        link = request.GET['link'],
                                        registrant = registrant,
                                        recipient = recipient,
                                        lobbyist = lobby,
            ) 
            contribution.save()
            lobbyist = str(contribution.lobbyist)

        continfo = {'amount': contribution.amount, 
                    'date': contribution.date.strftime("%B %d, %Y"), 
                    'recipient': str(contribution.recipient),
                    'lobbyist': lobbyist,
                    'cont_id': contribution.id,
        }
        continfo = json.dumps(continfo , separators=(',',':'))
        return HttpResponse(continfo, mimetype="application/json")  

    else:
        error = json.dumps({'error': 'failed'} , separators=(',',':'))
        return HttpResponse(error, mimetype="application/json") 


#creates disbursements 
@login_required(login_url='/admin')
def disbursement(request):
    if request.method == 'GET':
        try:
            date_obj = datetime.strptime(request.GET['date'], "%m/%d/%Y")
        except:
            error = json.dumps({'error': 'Incorrect date format'} , separators=(',',':'))
            return HttpResponse(error, mimetype="application/json")
        
        if date_obj > datetime.now():
            date_error = json.dumps({'error': 'date in the future'}, separators=(',',':'))
            return HttpResponse(date_error, mimetype="application/json")

        registrant = Registrant.objects.get(reg_id=int(request.GET['reg_id']))
        
        client = request.GET['client']
        if client == "None":
            error = json.dumps({'error': 'Please select a client.'} , separators=(',',':'))
            return HttpResponse(error, mimetype="application/json")
        client = Client.objects.get(id=int(request.GET['client']))
        
        purpose = cleantext(request.GET['purpose'])
        if request.GET['amount'] == '':
            error = json.dumps({'error': 'Disbursements must have an amount.'} , separators=(',',':'))
            return HttpResponse(error, mimetype="application/json")
        amount = cleanmoney(request.GET['amount'])

        disbursement = Disbursement(registrant = registrant,
                            client = client,
                            amount = amount,
                            purpose = purpose,
                            date = date_obj,
                            link = request.GET['link'],
        )
        disbursement.save()

        subcontractor_id = request.GET['subcontractor']
        if subcontractor_id != '' or None:
            subcontractor = Registrant.objects.get(reg_id = subcontractor_id )
            disbursement.subcontractor = subcontractor
            disbursement.save()

        try:
            clear = request.GET['do_not_clear']
        except:
            clear = "off"

        disinfo = {'amount': disbursement.amount,
                    'date': disbursement.date.strftime("%B %d, %Y"),
                    'registrant': str(disbursement.registrant),
                    'client': str(disbursement.client),
                    'dis_id': disbursement.id, 
                    'do_not_clear': clear,
        }
        disinfo = json.dumps(disinfo , separators=(',',':'))
        return HttpResponse(disinfo, mimetype="application/json")

         
    else:
        error = json.dumps({'error': 'failed'} , separators=(',',':'))
        return HttpResponse(error, mimetype="application/json") 


#creates gifts
@login_required(login_url='/admin')
def gift(request):
    if request.method == 'GET':
        try:
            date_obj = datetime.strptime(request.GET['date'], "%m/%d/%Y")
        except:
            date_error = json.dumps({'error': 'Incorrect date format'}, separators=(',',':'))
            return HttpResponse(date_error, mimetype="application/json")
        if date_obj > datetime.now():
            date_error = json.dumps({'error': 'date in the future'}, separators=(',',':'))
            return HttpResponse(date_error, mimetype="application/json")

        registrant = Registrant.objects.get(reg_id=int(request.GET['reg_id']))
        
        if request.GET['client'] == "None":
            error = json.dumps({'error': 'Please select a client.'} , separators=(',',':'))
            return HttpResponse(error, mimetype="application/json")
        clients = Client.objects.filter(id=int(request.GET['client']))
        
        purpose = cleantext(request.GET['purpose'])
        description = cleantext(request.GET['description'])
        
        gift= Gift(registrant =  registrant,
            date =  date_obj,
            purpose =  purpose,
            description =  description,
            link = request.GET['link'],
        )
        
        if request.GET['recipient'] != '':
           recipient = Recipient.objects.get(id=int(request.GET['recipient']))
           gift.recipient = recipient

        gift.save()
        client_names = ''
        for client in clients:
            gift.client.add(client)
            client_names = client_names + str(client.client_name) + ", " 
        
        giftinfo = {'client': client_names,
                    'date': gift.date.strftime("%B %d, %Y"), 
                    'description': gift.description
        }
        giftinfo = json.dumps(giftinfo , separators=(',',':'))
        return HttpResponse(giftinfo, mimetype="application/json")
         
    else:
        error = json.dumps({'error': 'failed'} , separators=(',',':'))
        return HttpResponse(error, mimetype="application/json") 

#tracks processing
@login_required(login_url='/admin')
def metadata(request):      
    if request.method == 'GET':
        if request.method == 'GET' and 'reviewed' in request.GET:
            reviewed = True
        else:
            reviewed = False
        if request.method == 'GET' and 'processed' in request.GET:
            processed = True
        else:
            processed = False
        if request.method == 'GET' and 'is_amendment' in request.GET:
            is_amendment = True
        else:
            is_amendment = False
        form = request.GET['form']
        link = request.GET['link']
        date_obj = date.today()

        try:
            end_date = datetime.strptime(request.GET['end_date'], "%m/%d/%Y")
            print_date = end_date.strftime("%B %d, %Y")
            print print_date
        except:
            end_date =  None

        metadata= MetaData(link = link,
            upload_date = date_obj,
            end_date = end_date,
            reviewed = reviewed,
            processed = processed,
            is_amendment = is_amendment,
            form = form,
            notes = request.GET['notes'],
        )
        metadata.save()

        document = Document.objects.get(url=link)
        if processed == True:
            document.processed = True
            document.save()
        else:
            document.processed = False
            document.save()

        metadata_info = json.dumps({'processed': processed, 'reviewed': reviewed} , separators=(',',':'))
        return HttpResponse(metadata_info, mimetype="application/json")
         
    else:
        error = json.dumps({'error': 'failed'} , separators=(',',':'))
        return HttpResponse(error, mimetype="application/json")        
    
#Easy fix forms

# Contacts
@login_required(login_url='/admin')
def amend_contact(request):        
    try:
        contact_id = int(request.GET['contact_id'])
        contact = Contact.objects.get(id=contact_id)

        contact.client = Client.objects.get(id=int(request.GET['client']))
        contact.contact_type = request.GET['contact_type']
        contact.description = cleantext(request.GET['description'])
        
        try:
            date_obj = datetime.strptime(request.GET['date'], "%m/%d/%Y")
        except:
            date_error = json.dumps({'error': 'Incorrect date format'}, separators=(',',':'))
            return HttpResponse(date_error, mimetype="application/json")
        contact.date = date_obj
        if date_obj > datetime.now():
            date_error = json.dumps({'error': 'date in the future'}, separators=(',',':'))
            return HttpResponse(date_error, mimetype="application/json")
        
        contact.save()
        # add additional recipients
        try:
            recipients = request.GET['recipient']
            if "," in recipients:
                recipients = recipients.split(',')
            else:
                recipients = [recipients]
        
        except:
            recipients = None
        
        if recipients != None and recipients != ['']:
            print recipients
            for r in recipients:
                recipient = Recipient.objects.get(id=int(r))
                if recipient not in contact.recipient.all():
                    contact.recipient.add(recipient)
        
        # add additional lobbyists
        try:
            lobbyists = request.GET.getlist('lobbyist')
        except:
            try:
                lobbyists = request.GET['lobbyist']
            except:
                lobbyists = None
        
        print lobbyists, "lobbyist"
        
        if lobbyists != None:
            for l in lobbyists:
                l = int(l)
                lobbyist = Lobbyist.objects.get(id=l)
                print lobbyist
                if lobbyist in contact.lobbyist.all():
                    pass
                else:
                    contact.lobbyist.add(lobbyist)
                    

        # finding redirect info
        url = str(contact.link)
        doc = Document.objects.get(url=url)
        form_id = int(doc.id)
        doc_type = str(doc.doc_type)
        
        if doc_type == "Supplemental":
            return supplemental_contact(request, form_id)

        if doc_type == "Amendment":
            return return_big_form(request, form_id)
    
    except:
        error = json.dumps({'error': 'failed'} , separators=(',',':'))
        return HttpResponse(error, mimetype="application/json") 

@login_required(login_url='/admin')
def contact_remove_lobby(request):
    if request.method == 'GET': 
        contact_id = int(request.GET['contact_id'])
        lobby_id = int(request.GET['lobbyist'])
        lobbyist = Lobbyist.objects.get(id=lobby_id)
        contact = Contact.objects.get(id=contact_id)
        contact.lobbyist.remove(lobbyist)

        info = json.dumps({'lobby_id': lobby_id}, separators=(',',':'))
        return HttpResponse(info, mimetype="application/json")

@login_required(login_url='/admin')
def contact_remove_recip(request):
    if request.method == 'GET': 
        contact_id = int(request.GET['contact_id'])
        recip_id = int(request.GET['recip'])
        recipient = Recipient.objects.get(id=recip_id)
        contact = Contact.objects.get(id=contact_id)
        
        contact.recipient.remove(recipient)

        info = json.dumps({'recip_id': recip_id}, separators=(',',':'))
        return HttpResponse(info, mimetype="application/json")

@login_required(login_url='/admin')
def amend_payment(request):
    if request.method == 'GET':
        payment_id = request.GET['pay_id']
        client = Client.objects.get(id=int(request.GET['client']))
        reg_id = Registrant.objects.get(reg_id=int(request.GET['reg_id']))
        
        try:
            date_obj = datetime.strptime(request.GET['date'], "%m/%d/%Y")
        except:
            date_error = json.dumps({'error': 'Incorrect date format'}, separators=(',',':'))
            return HttpResponse(date_error, mimetype="application/json")
        if date_obj > datetime.now():
            date_error = json.dumps({'error': 'date in the future'}, separators=(',',':'))
            return HttpResponse(date_error, mimetype="application/json")

        if request.method == 'GET' and 'fee' in request.GET:
            fee = True
        else:
            fee = False

        payment = Payment.objects.get(id=payment_id)
        payment.client = client
        payment.registrant = reg_id
        payment.fee = fee
        payment.amount = cleanmoney(request.GET['amount'])
        payment.purpose = cleantext(request.GET['purpose'])
        payment.date = date_obj
        
        payment.save()
        print "SAVING"

        subcontractor_id = request.GET['subcontractor']
        if subcontractor_id != '' or None:
            subcontractor = Registrant.objects.get(reg_id = subcontractor_id )
            payment.subcontractor = subcontractor
            payment.save()
        
        url = str(payment.link)
        doc = Document.objects.get(url=url)
        form_id = int(doc.id)
        doc_type = str(doc.doc_type)

        if doc_type == "Supplemental":
            return supplemental_payment(request, form_id)

        if doc_type == "Registration":
            return registration_payment(request, form_id)

        if doc_type == "Amendment":
            return return_big_form(request, form_id)


@login_required(login_url='/admin')
def payment_remove_sub(request):
    if request.method == 'GET':
        payment_id = int(request.GET['payment_id'])
        payment = Payment.objects.get(id=payment_id)
        payment.subcontractor = None
        payment.save()

        info = json.dumps({'payment_id': payment_id}, separators=(',',':'))
        return HttpResponse(info, mimetype="application/json")

@login_required(login_url='/admin')
def amend_disbursement(request):
    if request.method == 'GET':
        dis_id = request.GET['dis_id']
        dis = Disbursement.objects.get(id=dis_id)

        date_obj = datetime.strptime(request.GET['date'], "%m/%d/%Y")
        if date_obj > datetime.now():
            date_error = json.dumps({'error': 'date in the future'}, separators=(',',':'))
            return HttpResponse(date_error, mimetype="application/json")

        dis.date = date_obj
        dis.registrant = Registrant.objects.get(reg_id=int(request.GET['reg_id']))
        dis.client = Client.objects.get(id=int(request.GET['client']))
        dis.purpose = cleantext(request.GET['purpose'])
        dis.amount = cleanmoney(request.GET['amount'])

        subcontractor_id = request.GET['subcontractor']
        if subcontractor_id != '' and subcontractor_id != None:
            subcontractor = Registrant.objects.get(reg_id = subcontractor_id )
            dis.subcontractor = subcontractor
        
        dis.save()

        url = str(dis.link)
        doc = Document.objects.get(url=url)
        form_id = int(doc.id)
        doc_type = str(doc.doc_type)
        
        if doc_type == "Supplemental":
            return supplemental_disbursement(request, form_id)

        if doc_type == "Registration":
            return registration_disbursement(request, form_id)

        if doc_type == "Amendment":
            return return_big_form(request, form_id)


@login_required(login_url='/admin')
def disbursement_remove_sub(request):
    if request.method == 'GET':
        disbursement_id = int(request.GET['disbursement_id'])
        disbursement = Disbursement.objects.get(id=disbursement_id)
        disbursement.subcontractor = None
        disbursement.save()

        info = json.dumps({'disbursement_id': disbursement_id}, separators=(',',':'))
        return HttpResponse(info, mimetype="application/json")

@login_required(login_url='/admin')
def amend_contribution(request):
    if request.method == 'GET':
        contribution = Contribution.objects.get(id=request.GET['cont_id'])

        try:
            date_obj = datetime.strptime(request.GET['date'], "%m/%d/%Y")
        except:
            date_error = json.dumps({'error': 'Incorrect date format'}, separators=(',',':'))
            return HttpResponse(date_error, mimetype="application/json")
        if date_obj > datetime.now():
            date_error = json.dumps({'error': 'date in the future'}, separators=(',',':'))
            return HttpResponse(date_error, mimetype="application/json")

        contribution.amount = cleanmoney(request.GET['amount'])
        contribution.date = date_obj
        
        if request.GET['recipient'] != '' and request.GET['recipient'] != None:
            contribution.recipient = Recipient.objects.get(id=int(request.GET['recipient']))
        
        lobby = request.GET['lobbyist']
        if lobby != None and lobby != '':   
            contribution.lobbyist = Lobbyist.objects.get(id=int(request.GET['lobbyist']))
        else:
            contribution.lobbyist = None

        contribution.save()

        url = str(contribution.link)
        doc = Document.objects.get(url=url)
        form_id = int(doc.id)
        doc_type = str(doc.doc_type)
        
        if doc_type == "Supplemental":
            return supplemental_contibution(request, form_id)

        if doc_type == "Registration":
            return registration_contribution(request, form_id)

        if doc_type == "Amendment":
            return return_big_form(request, form_id)


