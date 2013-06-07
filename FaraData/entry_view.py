import re
from datetime import datetime, date

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse

from FaraData.models import * #LobbyistForm, ClientForm, RegForm, RecipientForm, ContactForm, PaymentForm, ContributionForm, Disbursement, DisbursementForm

#change GET to POST, but GET is better for debugging

# this needs to be passed in to the form but hard coding for now-
def doc_id():
    url = "http://www.fara.gov/docs/4929-Supplemental-Statement-20130227-15.pdf"
    id = url[25:29]
    return (url, id)
      
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
        dis_list.append([dis.client, dis.amount] ) 
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
    m = MetaData.objects.get(link=url)
    meta_list = [ m.reviewed, m.processed, m.upload_date, m.is_amendment, m.notes] 
    return meta_list
    

def index(request):
    lobby_form = LobbyistForm()
    client_form = ClientForm()
    reg_form = RegForm()
    recipient_form = RecipientForm()
    #options for the forms
    all_clients = Client.objects.all()
    all_lobbyists = Lobbyist.objects.all()
    all_recipients = Recipient.objects.all()
    #for displaying information already in the system
    url, reg_num, = doc_id()
    reg_object = reg_info(reg_num)
    contact_list = contact_info(url)
    dis_list = dis_info(url)
    pay_list = pay_info(url)
    cont_list = cont_info(url)
    gift_list = gift_info(url)
    meta_list = meta_info(url)
    
    return render(request, 'entry_form.html',{
        'recipient_form': recipient_form,
        'lobby_form': lobby_form,
        'client_form': client_form,
        'reg_form': reg_form,
        #options for forms
        'all_clients': all_clients,
        'all_lobbyists': all_lobbyists,
        'all_recipients': all_recipients,
        'reg_num': reg_num,
        'url': url, 
        'reg_object': reg_object,
        'contact_list': contact_list,
        'dis_list' : dis_list,
        'gift_list': gift_list,
        'pay_list' : pay_list,
        'cont_list' : cont_list,
        'meta_list' : meta_list,
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
            recipient.save()
            return render(request, 'success.html', {'status': form.cleaned_data['name']}) 
            
        else:
            return render(request, 'success.html', {'status': 'failed'})

            
# creates a new lobbyist using pre-made form        
def lobbyist(request):
    if request.method == 'GET':
        form = LobbyistForm(request.GET)
        if form.is_valid():
            lobby = Lobbyist(lobbyist_name = form.cleaned_data['lobbyist_name'], lobby_id = form.cleaned_data['lobby_id'])
            lobby.save()
            return render(request, 'success.html', {'status': form.cleaned_data['lobby_id']}) 
         
        else:
            return render(request, 'success.html', {'status': 'failed'})

### multiples not working 
# assigns a lobbyist or lobbyists to a reg. all_lobbyists
def reg_lobbyist(request):
    if request.method == 'GET': 
        reg_id = request.GET['reg_id']
        
        lobbyists = request.GET.getlist('lobbyists')
        if not lobbyists:
            lobbyists = [request.GET.get('lobbyists'),]
            
        message = ''
        registrant = Registrant.objects.get(reg_id=reg_id)
        for l_id in lobbyists:
            lobbyist = Lobbyist.objects.get(id=l_id)
            if lobbyist not in registrant.lobbyists.all():
                registrant.lobbyists.add(lobbyist)
                message += 'We added %s to lobbyists.' % l_id
            else:
                message += '%s was already in the lobbyists' % l_id
            return render(request, 'success.html', {'status': 'yay', 'message': message}) 
         
        else:
            return render(request, 'success.html', {'status': 'failed'})

#creates a new client
def client(request):
    if request.method == 'GET': # If the form has been submitted...
        form = ClientForm(request.GET) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            client = Client(client_name = form.cleaned_data['client_name'], 
                            location = form.cleaned_data['location'],
                            address1 = form.cleaned_data['address1'],
                            city = form.cleaned_data['city'],
                            state = form.cleaned_data['state'],
                            country = form.cleaned_data['country'],
            )
            client.save()
            registrant = Registrant.objects.get(reg_id=request.GET['reg_id'])
            if client not in registrant.clients.all():
                registrant.clients.add(client)
            return render(request, 'success.html', {'status': form.cleaned_data['client_name']}) 
         
        else:
            return render(request, 'success.html', {'status': 'failed'})


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

                  
#adds client to registrant 
def reg_client(request):
    if request.method == 'GET': # If the form has been submitted...
        reg_id = request.GET['reg_id'] # A form bound to the POST data
        clients = request.GET.getlist('clients')      
        message = ''
        registrant = Registrant.objects.get(reg_id=reg_id)
        for c_id in clients:
            client = Client.objects.get(id=c_id)
            if client not in registrant.clients.all():
                registrant.clients.add(client)
                message += 'We added %s to clients.' % c_id
            else:
                message += '%s was already in the clients' % c_id
            if client in registrant.terminated_clients.all():
                registrant.terminated_clients.remove(client) 
        return render(request, 'success.html', {'status': 'yay', 'message': message}) 
         
    else:
        return render(request, 'success.html', {'status': 'failed'})


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
            
        recipients_ids = request.GET.getlist('recipient')
        if not recipients_ids:
            recipients_ids = [request.GET.get('recipient'),]
        
        client = Client.objects.get(id=int(request.GET['client']))
        reg_id = Registrant.objects.get(reg_id=int(request.GET['reg_id']))
        date_obj = datetime.strptime(request.GET['date'], "%m/%d/%Y")
        recipients = Recipient.objects.filter(id__in=recipients_ids)
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

        for r in recipients:
            if r not in contact.recipient.all():
                contact.recipient.add(r)
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
    
        
        
        
