import re
import json
import dateutil
import dateutil.parser
from datetime import datetime, date
import reversion

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from FaraData.models import * 
from fara_feed.models import Document
from FaraData import spread_sheets 

## Section for functions that create variables for the templates 
    
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
def contact_info(url, page):
    contact_objects = Contact.objects.filter(link = url)
    
    paginator = Paginator(contact_objects, 20)
    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)

    contact_list = []
    for con in data:
        con_id = int(con.id)
        for recipient in con.recipient.all():
            contact_list.append([recipient.title, recipient.name, recipient.agency, con.date, con_id ])
    return (contact_list, data)

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
        gift = [g.description, g.date, g.id]
        for g in g.client.all():
            gift.append(g.client_name)
        gift_list.append(gift)
        
    return (gift_list)

def client_reg_info(reg):
    client_list = []
    try:
        clients = reg.clients.all()
        for c in clients:
            c_name = c.client_name
            c_type = c.client_type
           
            try:
                d = ClientReg.object.get(reg_id=reg.reg_id, client_id=c.id)
                c_dis = d.discription
                p_con = d.primary_contractor_id
            except:
                c_dis = ''
                p_con = ''
            
            client = [c_name, c_type, c_dis, p_con]
            client_list.append(client)
    except:
        pass
    return client_list

#finds meta data attached to form 
def meta_info(url):
    try:
        m = MetaData.objects.get(link=url)
        end_date = m.end_date.strftime('%m/%d/%Y')
        meta_list = [ m.reviewed, m.processed, m.upload_date, m.is_amendment, m.notes, end_date] 
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

## Section for rendering pages

#all in one supplemental data entry form- good for amendments
def return_big_form(request, form_id):
        url, reg_id, s_date = doc_id(form_id)
        #for displaying information already in the system
        reg_object = reg_info(reg_id)
        one_client = oneclient(reg_object)
        page = request.GET.get('page')
        contact_list = contact_info(url, page)[0]
        c_page_data = contact_info(url, page)[1]
        dis_list = dis_info(url)
        pay_list = pay_info(url)
        cont_list = cont_info(url)
        gift_list = gift_info(url)
        meta_list = meta_info(url)
        client_reg = client_reg_info(reg_object)

        return render(request, 'FaraData/entry_form.html',{
            #options for forms
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
            'client_reg' : client_reg,
            'data': c_page_data,
        })

@login_required(login_url='/admin')
def index(request, form_id):
    return return_big_form(request, form_id)

#multi-step supplemental form
@login_required(login_url='/admin')
def supplemental_base(request, form_id):
    return render(request, 'FaraData/supplemental_base.html', {'form_id': form_id})   

@login_required(login_url='/admin')
def wrapper(request, form_id):
    url, reg_id, s_date = doc_id(form_id)
    reg_object = reg_info(reg_id)
    meta_list = meta_info(url)

    return render(request, 'FaraData/dynamic_form.html',{
        'reg_id' : reg_id,
        'reg_object': reg_object,
        'url': url,
        'form_id': form_id,
        's_date': s_date,
        'meta_list': meta_list,
    })

@login_required(login_url='/admin')
def supplemental_first(request, form_id):
    url, reg_id, s_date = doc_id(form_id)
    reg_object = reg_info(reg_id)
    meta_list = meta_info(url)

    return render(request, 'FaraData/supplemental_first.html',{
        'reg_id' : reg_id,
        'reg_object': reg_object,
        'url': url,
        'form_id': form_id,
        's_date': s_date,
        'meta_list': meta_list,
    })

@login_required(login_url='/admin')
def supplemental_contact(request, form_id):
    url, reg_id, s_date = doc_id(form_id)
    reg_object = reg_info(reg_id)
    page = request.GET.get('page')
    contact_list = contact_info(url, page)[0]
    data = contact_info(url, page)[1]
    one_client = oneclient(reg_object)

    return render(request, 'FaraData/supplemental_contact.html',{
        'reg_id' : reg_id,
        'reg_object': reg_object,
        'one_client': one_client,
        'url': url,
        'form_id': form_id,
        'contact_list': contact_list,
        'data': data,
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
    one_client = oneclient(reg_object)

    return render(request, 'FaraData/supplemental_gift.html',{
    'reg_id' : reg_id,
    'url': url,
    'form_id': form_id,
    'reg_object': reg_object,
    'gift_list': gift_list,
    'one_client' : one_client,
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

    return render(request, 'FaraData/supplemental_contribution.html',{
    'reg_id': reg_id,
    'url': url,
    'form_id': form_id,
    'reg_object': reg_object,
    'cont_list': cont_list,
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
def reg_wrapper(request, form_id):
    url, reg_id, s_date = doc_id(form_id)
    reg_object = reg_info(reg_id)

    return render(request, 'FaraData/dynamic_reg_form.html',{
        'reg_id' : reg_id,
        'reg_object': reg_object,
        'url': url,
        'form_id': form_id,
        's_date': s_date,
    })

@login_required(login_url='/admin')
def registration_first(request, form_id):
    url, reg_id, s_date = doc_id(form_id)
    reg_object = reg_info(reg_id)

    return render(request, 'FaraData/registration_first.html',{
        'reg_id' : reg_id,
        'reg_object': reg_object,
        'url': url,
        'form_id': form_id,
        's_date': s_date,
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
    reg_object = reg_info(reg_id)

    return render(request, 'FaraData/registration_gift.html',{
    'reg_id' : reg_id,
    'url': url,
    'form_id': form_id,
    'gift_list': gift_list,
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

    return render(request, 'FaraData/registration_contribution.html',{
    'reg_id': reg_id,
    'url': url,
    'form_id': form_id,
    'reg_object': reg_object,
    'cont_list': cont_list,
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
    meta_list = meta_info(url)
    one_client = oneclient(reg_object)
    client_reg = client_reg_info(reg_object)

    return render(request, 'FaraData/enter_AB.html',{
        'reg_id' : reg_id,
        'reg_object': reg_object,
        'url': url,
        'form_id': form_id,
        'meta_list': meta_list,
        's_date': s_date,
        'one_client': one_client,
        'client_reg': client_reg,
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
    try:
        date = contact.date.strftime('%m/%d/%Y')
    except:
        date = ''

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
def clone_contact(request, contact_id): 
    contact =  Contact.objects.get(id=contact_id)
    reg_object = reg_info(contact.registrant.reg_id)
    url = contact.link
    lobbyists = reg_object.lobbyists.all()
    current_lobby = contact.lobbyist.all()
    recipients = contact.recipient.all()
    try:
        date = contact.date.strftime('%m/%d/%Y')
    except:
        date = ''

    return render(request, 'FaraData/clone_contact.html',{
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
    
    try:
        date = payment.date
        date = date.strftime('%m/%d/%Y')
    except:
        date = ''
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
    
    try:
        date = disbursement.date
        date = date.strftime('%m/%d/%Y')
    except:
        date = ''
        
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
    
    try:
        date = contribution.date
        date = date.strftime('%m/%d/%Y')
    except:
        date = ''

    return render(request, 'FaraData/fix_contribution.html',{
        'contribution': contribution,
        'reg_object': reg_object,
        'url': url,
        'date': date,
        })

@login_required(login_url='/admin')
def fix_registrant(request, reg_id, form_id):
    reg = Registrant.objects.get(reg_id=reg_id)
    doc = Document.objects.get(id=form_id)
    url = doc.url

    return render(request, 'FaraData/fix_reg.html', {
        'reg' : reg,
        'form_id': form_id,
        'url' : url,
        })

@login_required(login_url='/admin')
def fix_gift(request, gift_id):
    gift = Gift.objects.get(id=gift_id)
    url = gift.link
    reg_object = reg_info(gift.registrant.reg_id)
    try:
        date = gift.date.strftime('%m/%d/%Y')
    except:
        date = ''
    for g in gift.client.all():
        client = g
    if len(gift.client.all()) < 1:
        client = ''
        

    return render(request, 'FaraData/fix_gift.html', {
        'gift': gift,
        'reg_object': reg_object,
        'url': url, 
        'date': date,
        'client': client,
        })


@login_required(login_url='/admin')
def fix_client(request, client_id):
    print "placeholder"

@login_required(login_url='/admin')
def add_state_employee(request):
    return render(request, 'FaraData/form_state_employee.html')

@login_required(login_url='/admin')
def add_journalist(request):
    return render(request, 'FaraData/form_add_journalist.html')

@login_required(login_url='/admin')
def merge_recipient_form(request):
    return render(request, 'FaraData/merge_recipient.html')

## cleaning functions

#data cleaning
def cleantext(text):
    if text != None:
        text = re.sub(' +',' ', text)
        text = re.sub('\\r|\\n','', text)
        text = text.strip()
        return text
    else:
        return None

def cleanmoney(money):
    money = money.strip()
    money = money.replace('$', '').replace(',', '')
    return money

def cleandate(date):
        if len(date) == 10:
            try:
                date_obj = datetime.strptime(date, "%m/%d/%Y")
                if date_obj > datetime.now():
                    date_error = json.dumps({'error': 'date in the future'}, separators=(',',':'))
                    return date_error
                else:
                    return date_obj
            except:
                date_error = json.dumps({'error': 'Incorrect date format'}, separators=(',',':'))
                return date_error
        elif date == None or date == '':
                no_date = json.dumps({'error': 'No date'}, separators=(',',':'))
                return no_date
        else:
            try:
                date.strip()
                date_obj = dateutil.parser.parse(date)
                if date_obj > datetime.now():
                    date_error = json.dumps({'error': 'date in the future'}, separators=(',',':'))
                    return date_error
                else:
                    return date_obj     

            except:
                date_error = json.dumps({'error': 'Incorrect date format'}, separators=(',',':'))
                return date_error

## Section for functions that process forms

#corrects stamp date
@login_required(login_url='/admin')
def stamp_date(request):
    if request.method == 'GET':
        date = cleandate(request.GET['stamp_date'])
        if type(date) != datetime:
            return HttpResponse(date, mimetype="application/json")

        form_id = request.GET['form_id']
        document = Document.objects.get(id = form_id)
        stamp = Document(id = document.id,
                        url = document.url,
                        reg_id = document.reg_id,
                        doc_type = document.doc_type,
                        stamp_date = date,
        )
        stamp.save()

        date = date.strftime("%B %d, %Y")
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
        crp_id = cleantext(request.GET['crp_id'])
        
        agency = cleantext(request.GET['agency'])
        if agency == "Congress":
            error = json.dumps({'error': '"Congress" is only allowed for members of Congress, please use "Congressional" for all other contacts.'}, separators=(',',':'))        
            return HttpResponse(error, mimetype="application/json")
        
        office_detail = cleantext(request.GET['office_detail'])
        name  = cleantext(request.GET['name'])
        title = cleantext(request.GET['title'])

        if crp_id == '' and agency == '' and office_detail == '' and name == '':
            error = json.dumps({'error': 'Please fill out form before submitting'}, separators=(',',':'))        
            return HttpResponse(error, mimetype="application/json")

        recipient = Recipient(crp_id = crp_id,
                            agency = agency,
                            office_detail = office_detail,
                            name  = name,
                            title = title, 
        )
        
        try:
            if request.GET['state_local'] == "on":
                recipient.state_local = True
        except:
            pass

        recipient.save()
        recip_choice = json.dumps({'name': recipient.name}, separators=(',',':'))        
        return HttpResponse(recip_choice, mimetype="application/json")
            

@login_required(login_url='/admin')
def recipient_journalist(request):
    if request.method == 'GET':
        office_detail = cleantext(request.GET['office_detail'])
        name  = cleantext(request.GET['name'])
        title = cleantext(request.GET['title'])
        if (name == None or name == '') and (office_detail == None or office_detail == ''):
            error = json.dumps({'error': 'Pleasse fill out name or publication before submitting'}, separators=(',',':'))        
            return HttpResponse(error, mimetype="application/json")

        if (name is None or name == '') and (office_detail is not None or office_detail != ''):
            name = office_detail

        recipient = Recipient(
                            agency = "Media",
                            office_detail = office_detail,
                            name  = name,
                            title = title, 
        )

        recipient.save()
        recip_choice = json.dumps({'name': recipient.name}, separators=(',',':'))        
        return HttpResponse(recip_choice, mimetype="application/json")
            
# creates a new lobbyist and adds it to Registrant  
@login_required(login_url='/admin')       
def lobbyist(request):
    if request.method == 'GET':
        lobbyist_name = cleantext(request.GET['lobbyist_name'])
        PAC_name = cleantext(request.GET['PAC_name'])

        pac_size = 0
        lobby_size = 0
        for p in PAC_name:
            pac_size = len(p)   
        for l in lobbyist_name:
            lobby_size = len (l)

        # wrapped error messages in list so they work the same as a successful variable in the JS
        if pac_size == 0 and lobby_size == 0:
            error = json.dumps([{'error': "must have lobbyist name or PAC name"}], separators=(',',':')) 
            return HttpResponse(error, mimetype="application/json")
        
        if pac_size >= 1 and lobby_size >= 1:
            error = json.dumps([{'error': "Is this a lobbyist or a PAC? Only fill out the name in the appropriate field"}], separators=(',',':')) 
            return HttpResponse(error, mimetype="application/json")
        
        reg_id = request.GET['reg_id']
        lobby = Lobbyist(lobbyist_name = lobbyist_name, 
                        PAC_name = PAC_name, 
                        # I would love to add but we don't have data entry time now
                        #lobby_id = request.GET['lobby_id'],
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

# assigns a lobbyist or lobbyists to a reg. 
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

#creates a new and adds it to the registrant 
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

        client = Client(client_name = cleantext(request.GET['client_name']), 
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

            client_choice = [{'name': client.client_name,'id': client.id,}]
            client_choice = json.dumps(client_choice, separators=(',',':')) 
                
            return HttpResponse(client_choice, mimetype="application/json")  
     
    else:
        HttpResponse(request, {'error': 'failed'})

@login_required(login_url='/admin')
def client_info(request):
    if request.method == 'GET': 
        client_id = int(request.GET['client'])
        reg_id = int(request.GET['reg_id'])
        link = request.GET['link']
        
        try:
            client = Client.objects.get(id = client_id)
        except:
            error = json.dumps({'error': 'Please select a client.'} , separators=(',',':'))
            return HttpResponse(error, mimetype="application/json")
        
        # the registrant that is described by this model
        reg = Registrant.objects.get(reg_id=reg_id)
        
        try:
            record = ClientReg.objects.get(reg_id=reg, client_id=client)
        
        except:
            record = ClientReg(
                            reg_id=reg, 
                            client_id=client,
                )
        
        record.link = link

        # if this registrant is hired by another registrant  
        try:
            primary_contractor = int(request.GET['primary_contractor'])
            primary = Registrant.objects.get(reg_id=primary_contractor)
            record.primary_contractor_id = primary
        except:
            pass
        
        # these are on 2 different form that usually come in together but I don't want them to overwrite the older entry when they come in separately 
        client_type = request.GET['client_type']
        if client_type != None and client_type != '' and client_type != "None":
            client.client_type = client_type
        
        description = request.GET['description']
        if description != None and description != '' and description != "None":
            record.description = description
        
        client.save()
        record.save()
        
        clientinfo = json.dumps({'client_name': client.client_name, 'client_id': client_id, 'client_type': request.GET['client_type'], 'description': request.GET['description']}, separators=(',',':'))
        return HttpResponse(clientinfo, mimetype="application/json")

@login_required(login_url='/admin')
def location(request):
    if request.method == 'GET': 
        location = Location(location = cleantext(request.GET['location']),
                            country_grouping = cleantext(request.GET['country']),
                            region = cleantext(request.GET['region']),
                            country_code = request.GET['iso']
        )
        location.save()
        location_info = json.dumps({'location': location.location, 'country': location.country_grouping, 'region': location.region} , separators=(',',':'))
        return HttpResponse(location_info, mimetype="application/json")

    else:
        error = json.dumps({'error': 'failed'} , separators=(',',':'))
        return HttpResponse(error, mimetype="application/json")

@login_required(login_url='/admin')
def new_registrant(request):
    if request.method == 'GET':
        registrant = Registrant(reg_id = request.GET['reg_id'],
                            reg_name = cleantext(request.GET['reg_name']),
                            address = cleantext(request.GET['address']),
                            city = cleantext(request.GET['city']),
                            state = cleantext(request.GET['state']),
                            zip_code = cleantext(request.GET['zip']),
                            country = cleantext(request.GET['country']),
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
        r = request.GET.get('recipient')
        if r == None or r == '':
            error = json.dumps({'error': 'Please select a recipient.'} , separators=(',',':'))
            return HttpResponse(error, mimetype="application/json")

        link = request.GET['link']
        if MetaData.objects.filter(link=link).exists():
            md = MetaData.objects.get(link=link)
        else:
            error = json.dumps({'error': 'Fill out supplemental end date. The first question on the Supplemental form.'} , separators=(',',':'))
            return HttpResponse(error, mimetype="application/json") 

        lobbyists_ids = request.GET.getlist('lobbyist')
        if not lobbyists_ids:
            lobbyists_ids = [request.GET.get('lobbyists'),]

        client = request.GET['client']
        if client == '':
            error = json.dumps({'error': 'Please select a client.'} , separators=(',',':'))
            return HttpResponse(error, mimetype="application/json")
        client = Client.objects.get(id=int(request.GET['client']))

        reg_id = Registrant.objects.get(reg_id=int(request.GET['reg_id']))
        
        lobbyists = Lobbyist.objects.filter(id__in=lobbyists_ids)
        description = cleantext(request.GET['description'])

        contact = Contact(registrant = reg_id,
                            contact_type = request.GET['contact_type'],
                            description = description,
                            link = link,
                            client = client,
                            meta_data = md,
        )

        date = cleandate(request.GET['date'])
        if type(date) == datetime:
            contact.date = date
            date = contact.date.strftime("%B %d, %Y")
        else:
            if date == '{"error":"No date"}':
                date = ''
            else:
                return HttpResponse(date, mimetype="application/json")

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

        contactinfo = {'date': date, 
                        'name': names, 
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
        if client == "":
            error = json.dumps({'error': 'Please select a client.'} , separators=(',',':'))
            return HttpResponse(error, mimetype="application/json")
        client = Client.objects.get(id=int(client))
        
        link = request.GET['link']
        if MetaData.objects.filter(link=link).exists():
            md = MetaData.objects.get(link=link)
        else:
            error = json.dumps({'error': 'Fill out supplemental end date. The first question on the Supplemental form.'} , separators=(',',':'))
            return HttpResponse(error, mimetype="application/json") 

        reg_id = Registrant.objects.get(reg_id=int(request.GET['reg_id']) )
            
        # if request.method == 'GET' and 'fee' in request.GET:
        #     fee = True
        # else:
        #     fee = False

        purpose = cleantext(request.GET['purpose'])
        amount = cleanmoney(request.GET['amount'])
        if amount == "None" or amount == '':
            error = json.dumps({'error': 'Amount required'} , separators=(',',':'))
            return HttpResponse(error, mimetype="application/json")
        
        payment = Payment(client = client,
                            registrant = reg_id,
                            # fee = fee,
                            amount = amount,
                            purpose = purpose,
                            link = request.GET['link'],
                            meta_data = md,
        )

        date = cleandate(request.GET['date'])
        
        if type(date) == datetime:
            payment.date = date
            payment.sort_date = date
        else:
            if date == '{"error":"No date"}':
                md = MetaData.objects.get(link=request.GET['link'])
                if md.end_date != None:
                    payment.sort_date = md.end_date
                    date = ''
                else: 
                    error = json.dumps({'error': 'Fill out supplemental end date. The first question on the form.'} , separators=(',',':'))
                    return HttpResponse(error, mimetype="application/json")
            else:
                return HttpResponse(date, mimetype="application/json")

        subcontractor_id = request.GET['subcontractor']
        if subcontractor_id != '' and subcontractor_id != None:
            subcontractor = Registrant.objects.get(reg_id = subcontractor_id )
            payment.subcontractor = subcontractor
        
        payment.save()

        try:
            clear = request.GET['do_not_clear']
        except:
            clear = "off"

        try:
            date = payment.date.strftime("%B %d, %Y")
        except:
            date = ''

        # return info to update the entry form
        payinfo = {"amount": payment.amount, 
                    "fee": payment.fee, 
                    "date": date, 
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
        r = request.GET.get('recipient')
        if r == None or r == '':
            error = json.dumps({'error': 'Please select a recipient.'} , separators=(',',':'))
            return HttpResponse(error, mimetype="application/json")

        date = cleandate(request.GET['date'])
        if type(date) != datetime:
            if date == '{"error":"No date"}':
                date = None
                date_string = ''
            else:
                return HttpResponse(date, mimetype="application/json")
        else:
            date_string = date.strftime("%B %d, %Y")

        link = request.GET['link']
        if MetaData.objects.filter(link=link).exists():
            md = MetaData.objects.get(link=link)
        else:
            error = json.dumps({'error': 'Fill out supplemental end date. The first question on the Supplemental form.'} , separators=(',',':'))
            return HttpResponse(error, mimetype="application/json")  

        registrant = Registrant.objects.get(reg_id=int(request.GET['registrant']))
        recipient = Recipient.objects.get(id=int(request.GET['recipient']))
        
        amount = cleanmoney(request.GET['amount'])
        
        lobby = request.GET['lobbyist']
        if lobby == None or lobby == '':       
            contribution = Contribution(amount = amount, 
                                        date = date, 
                                        link = request.GET['link'],
                                        registrant = registrant,
                                        recipient = recipient,
                                        meta_data = md,
            ) 
            contribution.save()
            lobbyist = None
            
        else:
            lobby = Lobbyist.objects.get(id=int(request.GET['lobbyist'])) 
            contribution = Contribution(amount = amount, 
                                        date = date, 
                                        link = request.GET['link'],
                                        registrant = registrant,
                                        recipient = recipient,
                                        lobbyist = lobby,
                                        meta_data = md,
            ) 
            contribution.save()
            lobbyist = str(contribution.lobbyist.lobbyist_name)
            
        try:
            clear = request.GET['do_not_clear']
        except:
            clear = "off"

        continfo = {'amount': contribution.amount, 
                    'date': date_string, 
                    'recipient': contribution.recipient.name,
                    'lobbyist': lobbyist,
                    'cont_id': contribution.id,
                    'do_not_clear': clear,
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
        registrant = Registrant.objects.get(reg_id=int(request.GET['reg_id']))
        
        link = request.GET['link']
        if MetaData.objects.filter(link=link).exists():
            md = MetaData.objects.get(link=link)
        else:
            error = json.dumps({'error': 'Fill out supplemental end date. The first question on the Supplemental form.'} , separators=(',',':'))
            return HttpResponse(error, mimetype="application/json") 

        client = request.GET['client']
        if client == "":
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
                            link = request.GET['link'],
                            meta_data = md,
        )

        date = cleandate(request.GET['date'])
        if type(date) == datetime:
            disbursement.date = date
            date = date.strftime("%B %d, %Y")
        # allows for empty dates that get filled in by stamp date later
        elif date == '{"error":"No date"}':
            date = ""
        else:
            return HttpResponse(date, mimetype="application/json")

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
                    'date': date,
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
        registrant = Registrant.objects.get(reg_id=int(request.GET['reg_id']))
        link = request.GET['link']
        if MetaData.objects.filter(link=link).exists():
            md = MetaData.objects.get(link=link)
        else:
            error = json.dumps({'error': 'Fill out supplemental end date. The first question on the Supplemental form.'} , separators=(',',':'))
            return HttpResponse(error, mimetype="application/json") 

        if request.GET['client'] == "None":
            error = json.dumps({'error': 'Please select a client.'} , separators=(',',':'))
            return HttpResponse(error, mimetype="application/json")
        clients = Client.objects.filter(id=int(request.GET['client']))
        
        purpose = cleantext(request.GET['purpose'])
        description = cleantext(request.GET['description'])
        
        gift= Gift(registrant =  registrant,
            purpose =  purpose,
            description =  description,
            link = request.GET['link'],
            meta_data = md,
        )
        
        date = cleandate(request.GET['date'])
        if type(date) == datetime:
            gift.date = date
            date = date.strftime("%B %d, %Y")
        elif date == '{"error":"No date"}':
            date = ""
        else:
            return HttpResponse(date, mimetype="application/json")

        if request.GET['recipient'] != '':
           recipient = Recipient.objects.get(id=int(request.GET['recipient']))
           gift.recipient = recipient

        gift.save()

        client_names = ''
        for client in clients:
            gift.client.add(client)
            client_names = client_names + str(client.client_name) + ", " 
        
        giftinfo = {'client': client_names,
                    'date': date, 
                    'description': gift.description,
                    'gift_id': gift.id,
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
            registrant = Registrant.objects.get(reg_id=int(request.GET['reg_id']))
        except:
            error = json.dumps({'error': 'Please fill out Registrant form below before submitting notes.'} , separators=(',',':'))
            return HttpResponse(error, mimetype="application/json") 

        metadata= MetaData(link = link,
            upload_date = date_obj,
            reviewed = reviewed,
            processed = processed,
            is_amendment = is_amendment,
            form = form,
            notes = request.GET['notes'],
        )
        
        document = Document.objects.get(url=link)
        

        #supplemental end date- needed for supplementals, and some amendments
        try:
            end_date = cleandate(request.GET['end_date'])
            if type(end_date) != datetime:
                if document.doc_type == "Supplemental":
                    return HttpResponse(end_date, mimetype="application/json")
                elif end_date == '{"error":"No date"}':
                    end_date = None
                else:
                    return HttpResponse(end_date, mimetype="application/json")
            else:
                metadata.end_date = end_date
        except:
            end_date = None
        metadata.save()

        
        if processed == True:
            document.processed = True
        else:
            document.processed = False
        document.save()
        
        if metadata.processed == True:
            spread_sheets.make_file(form)
            print "through"

        registrant.meta_data.add(metadata)
        registrant.save()
   
        metadata_info = json.dumps({'note': metadata.notes, 'do_not_clear': 'on'} , separators=(',',':'))
        return HttpResponse(metadata_info, mimetype="application/json")
        
    else:
        error = json.dumps({'error': 'failed'} , separators=(',',':'))
        return HttpResponse(error, mimetype="application/json")        
    
## Section for Easy fix forms

# Contacts
@login_required(login_url='/admin')
def amend_contact(request):        
    try:
        contact_id = int(request.GET['contact_id'])
        contact = Contact.objects.get(id=contact_id)

        contact.client = Client.objects.get(id=int(request.GET['client']))
        contact.contact_type = request.GET['contact_type']
        contact.description = cleantext(request.GET['description'])
        
        date = cleandate(request.GET['date'])
        if type(date) == datetime:
            contact.date = date
        elif date == '{"error":"No date"}':
            date = ""
        else:
            return HttpResponse(date, mimetype="application/json")
        
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

        if lobbyists != None:
            for l in lobbyists:
                l = int(l)
                lobbyist = Lobbyist.objects.get(id=l)
                if lobbyist in contact.lobbyist.all():
                    pass
                else:
                    contact.lobbyist.add(lobbyist)       

        sucess = json.dumps({'sucess': contact_id} , separators=(',',':'))
        return HttpResponse(sucess, mimetype="application/json")
    
    except:
        error = json.dumps({'error': 'failed'} , separators=(',',':'))
        return HttpResponse(error, mimetype="application/json") 

@login_required(login_url='/admin')
def make_clone_contact(request):        
    # try:
    contact_id = int(request.GET['contact_id'])
    original_contact = Contact.objects.get(id=contact_id)
    
    if int(request.GET['reg_id']) != int(original_contact.registrant.reg_id):
        error = json.dumps({'error': 'Registrant id error'} , separators=(',',':'))
        return HttpResponse(error, mimetype="application/json")
   
    dates = request.GET['date']
    dates = dates.split(',')

    for d in dates:
        date = cleandate(d)
        if type(date) == datetime:
            date = date
        elif date == '{"error":"No date"}':
            date = ""
        else:
            return HttpResponse(date, mimetype="application/json")
        print "date processed"

        client_id = request.GET['client']
        client = Client.objects.get(id=client_id)
        print "found client"

        contact = Contact(registrant = original_contact.registrant,
                        contact_type = request.GET['contact_type'],
                        description = request.GET['description'],
                        link = original_contact.link,
                        client = client,
                        meta_data = original_contact.meta_data,
                        date = date,
        )
        contact.save()
        
        if original_contact.lobbyist.exists():
            for lobbyist in original_contact.lobbyist.all(): 
                contact.lobbyist.add(lobbyist) 

        original_recipients = original_contact.recipient.all()
        print "found recips \n"
        for recipient in original_recipients:
            print "looping \n"
            print recipient
            contact.recipient.add(recipient)
            print recipient.name
        print "recips \n"
        contact.save()     
        print "saved \n"

    sucess = json.dumps({'sucess': contact_id} , separators=(',',':'))
    return HttpResponse(sucess, mimetype="application/json")

    # except:
    #     error = json.dumps({'error': 'failed'} , separators=(',',':'))
    #     return HttpResponse(error, mimetype="application/json") 

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
def delete_contact(request):
    if request.method == 'GET':
        contact_id = int(request.GET['contact_id'])
        contact = Contact.objects.get(id=contact_id)
        url = str(contact.link)
        contact.delete()

        doc = Document.objects.get(url=url)
        form_id = int(doc.id)
        doc_type = str(doc.doc_type)
        
        info = json.dumps({'contact_id': contact_id}, separators=(',',':'))
        return HttpResponse(info, mimetype="application/json")
    
    else:
        error = json.dumps({'error': 'failed'} , separators=(',',':'))
        return HttpResponse(error, mimetype="application/json") 
        

@login_required(login_url='/admin')
def amend_payment(request):
    if request.method == 'GET':
        payment_id = request.GET['pay_id']
        payment = Payment.objects.get(id=payment_id)
        client = Client.objects.get(id=int(request.GET['client']))
        reg_id = Registrant.objects.get(reg_id=int(request.GET['reg_id']))
        
        date = cleandate(request.GET['date'])
        if type(date) == datetime:
            payment.date = date
            payment.sort_date = date
        else:
            if date == '{"error":"No date"}':
                if MetaData.objects.filter(link=request.GET['link']).exists():
                    md = MetaData.objects.get(link=request.GET['link'])
                    if md.end_date != None:
                        payment.sort_date = md.end_date
                        date = ''
                    else: 
                        error = json.dumps({'error': 'Fill out supplemental end date. The first question on the form.'} , separators=(',',':'))
                        return HttpResponse(error, mimetype="application/json")
                else:
                    error = json.dumps({'error': 'Fill out supplemental end date. The first question on the form.'} , separators=(',',':'))
                    return HttpResponse(error, mimetype="application/json") 
            else:
                return HttpResponse(date, mimetype="application/json")


        if request.method == 'GET' and 'fee' in request.GET:
            fee = True
        else:
            fee = False

        payment.client = client
        payment.registrant = reg_id
        payment.fee = fee
        payment.amount = cleanmoney(request.GET['amount'])
        payment.purpose = cleantext(request.GET['purpose'])
        
        payment.save()

        subcontractor_id = request.GET['subcontractor']
        if subcontractor_id != '' or None:
            subcontractor = Registrant.objects.get(reg_id = subcontractor_id )
            payment.subcontractor = subcontractor
            payment.save()
        
        info = json.dumps({'payment_id': payment_id}, separators=(',',':'))
        return HttpResponse(info, mimetype="application/json")


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
def delete_payment(request):
    if request.method == 'GET':
        payment_id = int(request.GET['payment_id'])
        payment = Payment.objects.get(id=payment_id)
        url = payment.link
        payment.delete()

        doc = Document.objects.get(url=url)
        form_id = int(doc.id)
        doc_type = str(doc.doc_type)

        info = json.dumps({'payment_id': payment_id}, separators=(',',':'))
        return HttpResponse(info, mimetype="application/json")

@login_required(login_url='/admin')
def amend_disbursement(request):
    if request.method == 'GET':
        dis_id = request.GET['dis_id']
        dis = Disbursement.objects.get(id=dis_id)

        date = cleandate(request.GET['date'])
        if type(date) == datetime:
            dis.date = date
        elif date == '{"error":"No date"}':
            date = ""
        else:
            return HttpResponse(date, mimetype="application/json")

        dis.registrant = Registrant.objects.get(reg_id=int(request.GET['reg_id']))
        dis.client = Client.objects.get(id=int(request.GET['client']))
        dis.purpose = cleantext(request.GET['purpose'])
        dis.amount = cleanmoney(request.GET['amount'])

        subcontractor_id = request.GET['subcontractor']
        if subcontractor_id != '' and subcontractor_id != None:
            subcontractor = Registrant.objects.get(reg_id = subcontractor_id )
            dis.subcontractor = subcontractor
        
        dis.save()

        info = json.dumps({'disbursement_id': dis.id}, separators=(',',':'))
        return HttpResponse(info, mimetype="application/json")


@login_required(login_url='/admin')
def disbursement_remove_sub(request):
    if request.method == 'GET':
        disbursement_id = int(request.GET['disbursement_id'])
        disbursement = Disbursement.objects.get(id=disbursement_id)
        disbursement.subcontractor = None
        disbursement.save()

        info = json.dumps({'disbursement_id': disbursement.id}, separators=(',',':'))
        return HttpResponse(info, mimetype="application/json")

@login_required(login_url='/admin')
def delete_disbursement(request):
    if request.method == 'GET':
        disbursement_id = int(request.GET['disbursement_id'])
        disbursement = Disbursement.objects.get(id=disbursement_id)
        url = str(disbursement.link)
        disbursement.delete()

        doc = Document.objects.get(url=url)
        form_id = int(doc.id)
        doc_type = str(doc.doc_type)
        
        info = json.dumps({'disbursement_id': disbursement_id}, separators=(',',':'))
        return HttpResponse(info, mimetype="application/json")

@login_required(login_url='/admin')
def amend_contribution(request):
    if request.method == 'GET':
        contribution = Contribution.objects.get(id=request.GET['cont_id'])

        date = cleandate(request.GET['date'])
        if type(date) == datetime:
            contribution.date =  date
        elif date == '{"error":"No date"}':
            date = ""
        else:
            return HttpResponse(date, mimetype="application/json")

        contribution.amount = cleanmoney(request.GET['amount'])
        
        if request.GET['recipient'] != '' and request.GET['recipient'] != None:
            contribution.recipient = Recipient.objects.get(id=int(request.GET['recipient']))
        
        lobby = request.GET['lobbyist']
        if lobby != None and lobby != '':   
            contribution.lobbyist = Lobbyist.objects.get(id=int(request.GET['lobbyist']))
        else:
            contribution.lobbyist = None

        contribution.save()

        info = json.dumps({'contribution': contribution.id}, separators=(',',':'))
        return HttpResponse(info, mimetype="application/json")

@login_required(login_url='/admin')
def delete_contribution(request):
    if request.method == 'GET':
        contribution_id = int(request.GET['contribution_id'])
        contribution = Contribution.objects.get(id=contribution_id)
        url = str(contribution.link)
        contribution.delete()

        doc = Document.objects.get(url=url)
        form_id = int(doc.id)
        doc_type = str(doc.doc_type)
        
        info = json.dumps({'contribution': contribution.id}, separators=(',',':'))
        return HttpResponse(info, mimetype="application/json")

@login_required(login_url='/admin')
def amend_client(request):
    if request.method == 'GET':
        print "placeholder"

@login_required(login_url='/admin')
def amend_registrant(request):
    if request.method == 'GET':
        try:
            reg_id = int(request.GET['reg_id'])
            reg = Registrant.objects.get(reg_id=reg_id)
            reg.reg_name = request.GET['reg_name']
            reg.address = request.GET['address']
            reg.city = request.GET['city']
            reg.state = request.GET['state']
            reg.zip_code = request.GET['zip_code']
            reg.country = request.GET['country']
            reg.save()

            sucess = json.dumps({'sucess': reg.reg_name} , separators=(',',':'))
            return HttpResponse(sucess, mimetype="application/json")

        except:
            error = json.dumps({'error': 'failed'} , separators=(',',':'))
            return HttpResponse(error, mimetype="application/json") 


@login_required(login_url='/admin')
# this doesn't work @reversion.create_revision()
def amend_gift(request):
    g_id = int(request.GET['gift_id'])
    gift= Gift.objects.get(id=g_id)
    try:
        date = cleandate(request.GET['date'])
        if type(date) == datetime:
            gift.date =  date
        elif date == '{"error":"No date"}':
            pass
        else:
            return HttpResponse(date, mimetype="application/json") 
    except:
        pass

    gift.purpose = request.GET['purpose']
    gift.description = request.GET['description']
    
    client = request.GET['client']
    if client != '':
        client = Client.objects.get(id=int(request.GET['client']))
        gift.client.add(client)
    else:
        clients = gift.client.all()
        for c in clients:
            gift.client.remove(c)

    try:
        recip = request.GET['recipient']
        if recip != '':
            recip_obj = Recipient.objects.get(id=int(recip))
            gift.recipient = recip_obj
    except:
        pass
    
    gift.save()

    info = json.dumps({'gift_id': gift.id}, separators=(',',':'))
    return HttpResponse(info, mimetype="application/json")


@login_required(login_url='/admin')
# this doesn't work @reversion.create_revision()
def delete_gift(request):   
    
    gift= Gift.objects.get(id=request.GET['gift_id'])
    url = str(gift.link)
    gift.delete()

    doc = Document.objects.get(url=url)
    form_id = int(doc.id)
    doc_type = str(doc.doc_type)
    
    info = json.dumps({'gift_id': gift.id}, separators=(',',':'))
    return HttpResponse(info, mimetype="application/json")
        
@login_required(login_url='/admin')
# this doesn't work @reversion.create_revision()
def gift_remove_recip(request):
    if request.method == 'GET':
        gift = Gift.objects.get(id=request.GET['gift_id'])
        gift.recipient = None
        gift.save()

        info = json.dumps({'gift_id': gift.id}, separators=(',',':'))
        return HttpResponse(info, mimetype="application/json")

## Section for merging forms
@login_required(login_url='/admin')
def merge_recipients(request):
    if request.method == "GET":
        correct = request.GET.get('correct_recipient')
        if correct == None or correct == '':
            error = json.dumps({'error': 'Please select a correct recipient.'} , separators=(',',':'))
            return HttpResponse(error, mimetype="application/json")        
        correct = Recipient.objects.get(id=correct)
        fix_list = []
        wrong_ids = request.GET.get('wrong_recipient')
        wrong_list = wrong_ids.split(',')
        if str(correct.id) in wrong_list:
            error = json.dumps({'error': 'You listed the same entry as correct and incorrect. Please remove it from the list of flawed recipients.'} , separators=(',',':'))
            return HttpResponse(error, mimetype="application/json")
        for w in wrong_list:
            wrong = Recipient.objects.get(id=int(w))
            # contacts
            fix_contacts = Contact.objects.filter(recipient=wrong)
            for contact in fix_contacts:
                fix_list.append({contact.id:str(contact.description)})
                if correct not in contact.recipient.all():
                    contact.recipient.add(correct)
                contact.recipient.remove(wrong)
                contact.save()
            # contribution
            fix_contributions = Contribution.objects.filter(recipient=wrong)
            for contribution in fix_contributions:
                fix_list.append({contribution.id:str(contribution.amount)})
                contribution.recipient = correct
                contribution.save()
            # gift
            fix_gifts = Gift.objects.filter(recipient=wrong)
            for gift in fix_gifts:
                fix_list.append({gift.id:str(gift.description)})
                gift.recipient = correct
                gift.save()
        
        # delete after
        wrong.delete()

        info = json.dumps({'note': fix_list}, separators=(',',':'))
        return HttpResponse(info)



            
