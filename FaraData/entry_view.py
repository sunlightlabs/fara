import re
import json
from datetime import datetime, date


from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse

from FaraData.models import * #LobbyistForm, ClientForm, RegForm, RecipientForm, ContactForm, PaymentForm, ContributionForm, Disbursement, DisbursementForm
from fara_feed.models import Document

#change GET to POST, but GET is better for debugging

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
        dis_list.append([dis.client, dis.amount]) 
    return dis_list 

#finds payments attached to this form 
def pay_info(url):
    pay_objects = Payment.objects.filter(link = url) 
    pay_list = []
    for pay in pay_objects: 
        pay_list.append([pay.client, pay.amount, pay.fee, pay.date])
    return pay_list

#finds contacts attached to this form 
def contact_info(url):
    contact_objects = Contact.objects.filter(link = url)
    contact_list = []
    for con in contact_objects:
        for recipient in con.recipient.all():
            contact_list.append((recipient.title, recipient.name, recipient.agency, con.date))
    return (contact_list)

#finds contributions attached to this form        
def cont_info(url):
    cont_objects = Contribution.objects.filter(link = url) 
    cont_list = []
    for cont in cont_objects: 
        cont_list.append([cont.lobbyist, cont.amount, cont.recipient])
    return cont_list
               
#finds gifts attached to the form
def gift_info(url):
    gift_objects = Gift.objects.filter(link = url) 
    gift_list = []
    for g in gift_objects:
        gift = [g.discription, g.date]
        for g in g.client.all():
            gift.append(g.client_name)
        gift_list.append(gift)
    return (gift_list)

#finds meta data attached to form 
def meta_info(url):
    try:
        m = MetaData.objects.get(link=url)
        meta_list = [ m.reviewed, m.processed, m.upload_date, m.is_amendment, m.notes] 
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

#all in one supplemental data entry form- good for amendments
def index(request, form_id):
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
    contact_list = contact_info(url)
    dis_list = dis_info(url)
    pay_list = pay_info(url)
    cont_list = cont_info(url)
    gift_list = gift_info(url)
    meta_list = meta_info(url)
    
    return render(request, 'entry_form.html',{
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
    })

#multi-step supplemental form
def supplemental_base(request, form_id):
    return render(request, 'supplemental_base.html', {'form_id': form_id})   

def supplemental_first(request, form_id):
    url, reg_id, s_date = doc_id(form_id)
    reg_object = reg_info(reg_id)
    #reg_form = RegForm()
    all_clients = Client.objects.all()
    client_form = ClientForm()

    return render(request, 'supplemental_first.html',{
        'reg_id' : reg_id,
        'reg_object': reg_object,
        'url': url,
        #'reg_form': reg_form,
        'all_clients': all_clients,
        'client_form': client_form,
        'form_id': form_id,
        's_date': s_date,
    })

def supplemental_contact(request, form_id):
    url, reg_id, s_date = doc_id(form_id)
    reg_object = reg_info(reg_id)
    contact_list = contact_info(url)
    client_form = ClientForm()
    recipient_form = RecipientForm()
    all_recipients = Recipient.objects.all()
    all_lobbyists = Lobbyist.objects.all()

    return render(request, 'supplemental_contact.html',{
        'reg_id' : reg_id,
        'reg_object': reg_object,
        'url': url,
        'client_form': client_form,
        'form_id': form_id,
        'recipient_form': recipient_form,
        'all_recipients': all_recipients,
        'contact_list': contact_list,
        'all_lobbyists': all_lobbyists,
    })

def supplemental_payment(request, form_id):
    url, reg_id, s_date = doc_id(form_id)
    pay_list = pay_info(url)
    reg_object = reg_info(reg_id)

    return render(request, 'supplemental_payment.html',{
    'reg_id' : reg_id,
    'url': url,
    'pay_list' : pay_list,
    'reg_object': reg_object,
    'form_id': form_id,
    })

def supplemental_gift(request, form_id):
    url, reg_id, s_date = doc_id(form_id)
    gift_list = gift_info(url)
    reg_object = reg_info(reg_id)

    return render(request, 'supplemental_gift.html',{
    'reg_id' : reg_id,
    'url': url,
    'form_id': form_id,
    'reg_object': reg_object,
    'gift_list': gift_list,
    })

def supplemental_disbursement(request, form_id):
    url, reg_id, s_date = doc_id(form_id)
    reg_object = reg_info(reg_id)
    dis_list = dis_info(url)

    return render(request, 'supplemental_disbursement.html',{
    'reg_id' : reg_id,
    'url': url,
    'form_id': form_id,
    'reg_object': reg_object,
    'dis_list' : dis_list,
    })

def supplemental_contribution(request, form_id):
    url, reg_id, s_date = doc_id(form_id)
    reg_object = reg_info(reg_id)
    cont_list = cont_info(url)
    all_recipients = Recipient.objects.all()
    recipient_form = RecipientForm()

    return render(request, 'supplemental_contribution.html',{
    'reg_id': reg_id,
    'url': url,
    'form_id': form_id,
    'reg_object': reg_object,
    'cont_list': cont_list,
    'all_recipients': all_recipients,
    'recipient_form': recipient_form,
    })

def supplemental_last(request, form_id):
    url, reg_id, s_date= doc_id(form_id)
    meta_list = meta_info(url)

    return render(request, 'supplemental_last.html',{
    'reg_id' : reg_id,
    'url': url,
    'form_id': form_id,
    'meta_list': meta_list,
    })

# segmented registration form
def registration_base(request, form_id):
    return render(request, 'registration_base.html', {'form_id': form_id})   

def registration_first(request, form_id):
    url, reg_id, s_date = doc_id(form_id)
    reg_object = reg_info(reg_id)
    all_clients = Client.objects.all()
    client_form = ClientForm()

    return render(request, 'registration_first.html',{
        'reg_id' : reg_id,
        'reg_object': reg_object,
        'url': url,
        'all_clients': all_clients,
        'client_form': client_form,
        'form_id': form_id,
        's_date': s_date,
    })

def registration_contact(request, form_id):
    url, reg_id, s_date = doc_id(form_id)
    reg_object = reg_info(reg_id)
    contact_list = contact_info(url)
    client_form = ClientForm()
    recipient_form = RecipientForm()
    all_recipients = Recipient.objects.all()

    return render(request, 'registration_contact.html',{
        'reg_id' : reg_id,
        'reg_object': reg_object,
        'url': url,
        'client_form': client_form,
        'form_id': form_id,
        'recipient_form': recipient_form,
        'all_recipients': all_recipients,
        'contact_list': contact_list,
    })

def registration_payment(request, form_id):
    url, reg_id, s_date = doc_id(form_id)
    pay_list = pay_info(url)
    reg_object = reg_info(reg_id)

    return render(request, 'registration_payment.html',{
    'reg_id' : reg_id,
    'url': url,
    'pay_list' : pay_list,
    'reg_object': reg_object,
    'form_id': form_id,
    })

def registration_gift(request, form_id):
    url, reg_id, s_date = doc_id(form_id)
    gift_list = gift_info(url)

    return render(request, 'registration_gift.html',{
    'reg_id' : reg_id,
    'url': url,
    'form_id': form_id,
    'gift_list': gift_list,
    })

def registration_disbursement(request, form_id):
    url, reg_id, s_date = doc_id(form_id)
    reg_object = reg_info(reg_id)
    dis_list = dis_info(url)

    return render(request, 'registration_disbursement.html',{
    'reg_id' : reg_id,
    'url': url,
    'form_id': form_id,
    'reg_object': reg_object,
    'dis_list' : dis_list,
    })

def registration_contribution(request, form_id):
    url, reg_id, s_date = doc_id(form_id)
    reg_object = reg_info(reg_id)
    cont_list = cont_info(url)
    all_recipients = Recipient.objects.all()
    recipient_form = RecipientForm()

    return render(request, 'registration_contribution.html',{
    'reg_id': reg_id,
    'url': url,
    'form_id': form_id,
    'reg_object': reg_object,
    'cont_list': cont_list,
    'all_recipients': all_recipients,
    'recipient_form': recipient_form,
    })

def registration_last(request, form_id):
    url, reg_id, s_date = doc_id(form_id)
    meta_list = meta_info(url)

    return render(request, 'registration_last.html',{
    'reg_id' : reg_id,
    'url': url,
    'form_id': form_id,
    'meta_list': meta_list,
    })

def enter_AB(request, form_id):
    url, reg_id, s_date = doc_id(form_id)
    reg_object = reg_info(reg_id)
    #reg_form = RegForm()
    all_clients = Client.objects.all()
    client_form = ClientForm()
    meta_list = meta_info(url)

    return render(request, 'enter_AB.html',{
        'reg_id' : reg_id,
        'reg_object': reg_object,
        'url': url,
        #'reg_form': reg_form,
        'all_clients': all_clients,
        'client_form': client_form,
        'form_id': form_id,
        'meta_list': meta_list,
        's_date': s_date,
    })

#data cleaning
def cleantext(text):
    text = re.sub(' +',' ', text)
    text = re.sub('\\r|\\n','', text)
    return text

def cleanmoney(money):
    money = money.strip()
    money = money.replace('$', '').replace(',', '')
    return money
 
#corrects stamp date
def stamp_date(request):
    if request.method == 'GET':
        s_date = datetime.strptime(request.GET['stamp_date'], "%m/%d/%Y")
        form_id = request.GET['form_id']
        document = Document.objects.get(id = form_id)
        stamp = Document(id = document.id,
                        url = document.url,
                        reg_id = document.reg_id,
                        doc_type = document.doc_type,
                        stamp_date = s_date,
        )
        if s_date < datetime.now():
            stamp.save()
        else:
            return render(request, 'success.html', {'status': 'date in the future'})   

        return render(request, 'success.html', {'status': request.GET['stamp_date']})
    else:
        return render(request, 'success.html', {'status': 'failed'})
  
#creates a new recipient
def recipient(request):
    if request.method == 'GET':
        form = RecipientForm(request.GET)
        if form.is_valid():
            recipient = Recipient(bioguide_id = form.cleaned_data['bioguide_id'],
                                agency = form.cleaned_data['agency'],
                                office_detail = form.cleaned_data['office_detail'],
                                name  = form.cleaned_data['name'],
                                title = form.cleaned_data['title'], 
            )
            recipient.stamp_date.add()
            return render(request, 'success.html', {'status': form.cleaned_data['name']}) 
            
        else:
            return render(request, 'success.html', {'status': 'failed'})

            
# creates a new lobbyist and adds it to Registrant         
def lobbyist(request):
    if request.method == 'GET':
        reg_id = request.GET['reg_id']
        lobby = Lobbyist(lobbyist_name = request.GET['lobbyist_name'], 
                        PAC_name = request.GET['PAC_name'], 
                        lobby_id = request.GET['lobby_id'],
        )
        lobby.save()
        lobby_obj = Lobbyist.objects.get(id = lobby.id)
        reg_id = request.GET['reg_id']
        registrant = Registrant.objects.get(reg_id = reg_id)
        registrant.lobbyists.add(lobby_obj)
        #
        message = '<li><b>' + str(request.GET['lobbyist_name']) + '</b></li>'
        return render(request, 'success.html', {'status':'yes', 'message': message}) 
         
    else:
        return render(request, 'success.html', {'status': 'failed'})

# assigns a lobbyist or lobbyists to a reg. all_lobbyists
#### it is only adding the first one-- I thought this was fixed?

def reg_lobbyist(request):
    if request.method == 'GET': 
        reg_id = request.GET['reg_id']
        registrant = Registrant.objects.get(reg_id=reg_id)
        
        # lobbyists = request.GET.getlist('lobbyists')
        # if not lobbyists:
        #     lobbyists = [request.GET.get('lobbyists'),]
        message = ''  
        
        lobby_ids = request.GET.get('lobbyists')
        lobbyists =lobby_ids.split(',')
        for l_id in lobbyists:
            lobbyist = Lobbyist.objects.get(id=l_id)
            if lobbyist not in registrant.lobbyists.all():
                registrant.lobbyists.add(lobbyist)
                message += 'We added %s to lobbyists.' % l_id
            else:
                message += '%s was already in the lobbyists' % l_id

        return render(request, 'success.html', {'status': 'yay', 'message': message}) 

#creates a new client and adds it to the registrant 
def client(request):
    if request.method == 'GET': # If the form has been submitted...
        form = ClientForm(request.GET) # A form bound to the POST data
        if form.is_valid():
            client = Client(client_name = form.cleaned_data['client_name'], 
                            location = form.cleaned_data['location'],
                            address1 = form.cleaned_data['address1'],
                            city = form.cleaned_data['city'],
                            state = form.cleaned_data['state'],
                            country = form.cleaned_data['country'],
            )
            if Client.objects.filter(client_name = client.client_name).exists():
                error = json.dumps({'error': "name in system"}, separators=(',',':')) 
                return HttpResponse(error, mimetype="application/json")
            else:
                client.save()
                registrant = Registrant.objects.get(reg_id=request.GET['reg_id'])
                client_choice = [{'name': client.client_name,'id': client.id,}]
                client_choice = json.dumps(client_choice, separators=(',',':')) 
                
                if client not in registrant.clients.all():
                    registrant.clients.add(client)
                return HttpResponse(client_choice, mimetype="application/json")  
         
        else:
            HttpResponse(request, {'error': 'failed'})

#want to phase out this one because it doesn't auto suggest reg number
#creates a new registrant 
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
            return render(request, 'registrant_success.html', {'status': 'reg_name', 'reg': registrant})
        else:
            return render(request, 'success.html', {'status': form.errors}, status=400)

def new_registrant(request):
    if request.method == 'GET':
        registrant = Registrant(reg_id = request.GET['reg_id'],
                            reg_name = request.GET['reg_name'],
                            address = request.GET['address'],
                            city = request.GET['city'],
                            state = request.GET['state'],
                            zip = request.GET['zip'],
                            country = request.GET['country'],
                            )
        registrant.save()
        return render(request, 'registrant_success.html', {'status': 'reg_name', 'reg': registrant})
    else:
        return render(request, 'success.html', {'status': form.errors}, status=400)

                  
#adds existing client to registrant 
def reg_client(request):
    if request.method == 'GET': # If the form has been submitted...
        reg_id = request.GET['reg_id'] # A form bound to the POST data
        clients = request.GET.getlist('clients')      
        message = ''
        registrant = Registrant.objects.get(reg_id=reg_id)
        client_choices = []
        for c_id in clients:
            client = Client.objects.get(id=c_id)
            if client not in registrant.clients.all():
                registrant.clients.add(client)
                message += 'We added %s to clients.' % c_id
            else:
                message += '%s was already in the clients' % c_id
            if client in registrant.terminated_clients.all():
                registrant.terminated_clients.remove(client)
            client_choices.append({
                'name': client.client_name,
                'id': client.id
                })

        client_choices = json.dumps(client_choices, separators=(',',':'))
        return HttpResponse(client_choices, mimetype="application/json") 
         
    else:
        return render(request, 'choices.html', {'choices': client_choices})


#adds client as terminated in registrant 
def terminated(request):
    if request.method == 'GET': # If the form has been submitted...
        reg_id = request.GET['reg_id'] # A form bound to the POST data
        clients = request.GET.getlist('clients')
        message = ''
        registrant = Registrant.objects.get(reg_id=reg_id)
        for c_id in clients:
            client = Client.objects.get(id=c_id)
            if client not in registrant.terminated_clients.all():
                registrant.terminated_clients.add(client)
                if client in registrant.clients.all():
                    registrant.clients.remove(client)
                message += 'We added %s to terminated clients.' % c_id
            else:
                message += '%s was already in the terminated clients' % c_id
        return render(request, 'success.html', {'status': 'yay', 'message': message}) 
         
    else:
        return render(request, 'success.html', {'status': 'failed'})
        
        
#creates contact
def contact(request):
    if request.method == 'GET':
        
        lobbyists_ids = request.GET.getlist('lobbyist')
        if not lobbyists_ids:
            lobbyists_ids = [request.GET.get('lobbyists'),]

        client = Client.objects.get(id=int(request.GET['client']))
        reg_id = Registrant.objects.get(reg_id=int(request.GET['reg_id']))
        date_obj = datetime.strptime(request.GET['date'], "%m/%d/%Y")
        lobbyists = Lobbyist.objects.filter(id__in=lobbyists_ids)
        description = cleantext(request.GET['description'])
        
        contact = Contact(
                            registrant = reg_id,
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
        
        for r in recipients:
            recip = Recipient.objects.get(id=r)
            if recip not in contact.recipient.all():
                contact.recipient.add(recip)
        
        for l in lobbyists:
            if l not in contact.lobbyist.all():
                contact.lobbyist.add(l)
        
        return render(request, 'success.html', {'status': 'contact_name'}) 
     
    else:
        return render(request, 'success.html', {'status': 'failed'})
        
        
#creates payment
def payment(request):
    if request.method == 'GET':
        client = Client.objects.get(id=int(request.GET['client']))
        reg_id = Registrant.objects.get(reg_id=int(request.GET['reg_id']) )
        message = ''
        date_obj = datetime.strptime(request.GET['date'], "%m/%d/%Y")
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
        return render(request, 'success.html', {'status': 'amount'})
        
    else:
        return render(request, 'success.html', {'status': 'failed'})


#creates contributions
def contribution(request):
    if request.method == 'GET':
        date_obj = datetime.strptime(request.GET['date'], "%m/%d/%Y")
        registrant = Registrant.objects.get(reg_id=int(request.GET['registrant']))
        recipient = Recipient.objects.get(id=int(request.GET['recipient']))
        lobby = Lobbyist.objects.get(id=int(request.GET['lobbyist']))
        amount = cleanmoney(request.GET['amount'])
               
        contribution = Contribution(amount = amount, 
                                    date = date_obj, 
                                    link = request.GET['link'],
                                    registrant = registrant,
                                    recipient = recipient,
                                    lobbyist = lobby, 
        ) 
        contribution.save()
        return render(request, 'success.html', {'status': 'amount'}) 
        
    else:
        return render(request, 'success.html', {'status': 'failed'})


#creates disbursements 
def disbursement(request):
    if request.method == 'GET':
        date_obj = datetime.strptime(request.GET['date'], "%m/%d/%Y")
        registrant = Registrant.objects.get(reg_id=int(request.GET['reg_id']))
        client = Client.objects.get(id=int(request.GET['client']))
        message = ''
        purpose = cleantext(request.GET['purpose'])
        amount = cleanmoney(request.GET['amount'])
        
        disbursement = Disbursement(
                            registrant = registrant,
                            client = client,
                            amount = amount,
                            purpose = purpose,
                            date = date_obj,
                            link = request.GET['link'],
        )
        disbursement.save()
            
        return render(request, 'success.html', {'status': 'amount'}) 
         
    else:
        return render(request, 'success.html', {'status': 'failed'})


#creates gifts
def gift(request):
    if request.method == 'GET':
        date_obj = datetime.strptime(request.GET['date'], "%m/%d/%Y")
        registrant = Registrant.objects.get(reg_id=int(request.GET['reg_id']))
        clients = Client.objects.filter(id=int(request.GET['client']))
        message = []
        purpose = cleantext(request.GET['purpose'])
        discription = cleantext(request.GET['discription'])
        
        gift= Gift(
            registrant =  registrant,
            date =  date_obj,
            purpose =  purpose,
            discription =  discription,
            link = request.GET['link'],
        )
        gift.save()
        for client in clients:
            gift.client.add(client)
            message += 'We added %s to clients.' % client
            
        return render(request, 'success.html', {'status': 'yay', 'message': message}) 
         
    else:
        return render(request, 'success.html', {'status': 'failed'})

#tracks processing
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
        date_obj = date.today()
        metadata= MetaData(
            link = request.GET['link'],
            upload_date = date_obj,
            reviewed = reviewed,
            processed = processed,
            is_amendment = is_amendment,
            form = request.GET['form'],
            notes = request.GET['notes'],
        )
        metadata.save()
        return render(request, 'success.html', {'status': 'yay'}) 
         
    else:
        return render(request, 'success.html', {'status': 'failed'})        
    
        
        
        
