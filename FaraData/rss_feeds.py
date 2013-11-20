from datetime import datetime, date

from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
# from django.utils.safestring import SafeData, mark_safe
from django.utils.html import format_html
from FaraData.models import *
from fara_feed.models import *

base_url = "http://54.234.244.182"

doc_type = ''
link = ''
upload_date = ''

def find_reg(item):
    reg_id = re.sub('-','', item.url[25:29])
    reg_id = re.sub('S','', reg_id)
    reg_id = re.sub('L','', reg_id)
    reg = Registrant.objects.get(reg_id=reg_id)
    return reg

def find_regMD(item):
    if item.link[:4] == "http":
        reg_id = re.sub('-','', item.link[25:29])
        reg_id = re.sub('S','', reg_id)
        reg_id = re.sub('L','', reg_id)
        reg = Registrant.objects.get(reg_id=reg_id)
        return reg
    else:
        print item.link 
        reg_id = re.sub('-','', item.link[15:19])
        reg_id = re.sub('S','', reg_id)
        reg_id = re.sub('L','', reg_id)
        reg = Registrant.objects.get(reg_id=reg_id)
        return reg        

def compute_pay(url):
    payments = Payment.objects.filter(link=url).count()
    if payments > 0:
        pay_objects = Payment.objects.filter(link=url)
        doc = Document.objects.get(url=url)
        total = 0
        for pay in pay_objects:
            amount = pay.amount
            if amount != '':
                total = total + amount
        payment = ' Total payments this report: $ %.2f Download detailed payment spreadsheet: %s/payment_csv/%d ' %(total, base_url, doc.id)
        return payment
    else:
        payment = None
        return payment

#@login_required(login_url='/admin')
class LatestEntriesFeed(Feed):
    title = "Latest entries in the Foreign lobbying database"
    link = base_url + "/latest/rss/"
    description = "Most recent Foreign Agent Registration Act documents, including a link to the source document, client list and summary information."

    def items(self):
        return Document.objects.filter(processed=True).order_by('-stamp_date')[:25]

    def item_link(self, item):
        return item.url
    
    def item_guid(self, item):
        return item.url

    def item_pubdate(self, item):
        return datetime.combine(item.stamp_date, datetime.min.time())


    def item_description(self, item):
        info = "Date received: %s " %(item.stamp_date)
        link = item.url
        doc_type = item.doc_type
        reg = find_reg(item)

        client = ''
        clients = reg.clients.all()
        for c in clients:
            client = client + c.client_name + "; "
        
        if len(client) > 0:
            info = info + "Active clients: %s"%(client)
        
        terminated = ''
        terminated_clients = reg.terminated_clients.all()
        for c in terminated_clients:
            terminated = c.client_name + "; "
        if len(terminated) > 0:
            info = info + "Terminated clients: %s"%(terminated)

        if doc_type == "Exhibit AB":
            try:
                new_client = ClientReg.objects.get(link=link)
                info = info + "New client: " + new_cient
            except:
                pass

        if doc_type == "Supplemental":
            pay_info = compute_pay(link)
            if pay_info != None:
                info = info + pay_info

            contacts = Contact.objects.filter(link=link).count()
            if contacts > 0:
                info = info + ' Number of contacts: %i Download detailed contact spreadsheet: %s/contact_csv/%d ' %(contacts, base_url, item.id)

        if doc_type == "Registration":
            pay_info = compute_pay(link)
            if pay_info != None:
                info = info + pay_info

            contacts = Contact.objects.filter(link=link).count()
            if contacts > 0:
                info = info + ' Number of contacts: %i Download detailed contact spreadsheet: %s/contact_csv/%d ' %(contacts, base_url, item.id)

        return info

    def item_title(self, item):
        reg = find_reg(item)
        doc_type = item.doc_type
        name = reg.reg_name
        title = "%s-- %s %s" %(name, doc_type, upload_date)
        return title


class DataEntryFeed(Feed):
    title = "Latest entered documents in the Foreign lobbying database"
    link = base_url + "/entry/rss/"
    description = "Most recently added to our data, regardless of when it was originally posted"

    def items(self):
        return MetaData.objects.filter(processed=True).order_by('-upload_date')[:25]

    def item_link(self, item):
        return item.link

    def item_guid(self, item):
         return item.link

    def item_pubdate(self, item):
        if item.notes == "Legacy data":
            legacy_date = date(2013, 6, 1)
            return datetime.combine(legacy_date, datetime.min.time())
        else:
            print item.link
            return datetime.combine(datetime.now(), datetime.min.time())

    def item_description(self, item):
        doc = Document.objects.get(url=item.link)
        doc_type = doc.doc_type
        info = "Date received: %s " %(doc.stamp_date)
        link = item.link
        reg = find_regMD(item)

        client = ''
        clients = reg.clients.all()
        for c in clients:
            client = client + c.client_name
        if len(client) > 0:
            info = info + " Active clients: %s"%(client)
        
        terminated = ''
        terminated_clients = reg.terminated_clients.all()
        for c in terminated_clients:
            terminated = c.client_name
        if len(terminated) > 0:
            info = info + " Terminated clients: %s"%(terminated)

        if doc_type == "Exhibit AB":
            try:
                new_client = ClientReg.objects.get(link=link)
                info = info + " New client: " + new_cient
            except:
                pass

        if doc_type == "Supplemental":
            pay_info = compute_pay(link)
            if pay_info != None:
                info = info + pay_info
            
            contacts = Contact.objects.filter(link=link).count()
            if contacts > 0:
                info = info + ' Number of contacts: %i Download detailed contact spreadsheet: %s/contact_csv/%d ' %(contacts, base_url, doc.id)

        if doc_type == "Registration":
            pay_info = compute_pay(link)
            if pay_info != None:
                info = info + pay_info
            
            contacts = Contact.objects.filter(link=link).count()
            if contacts > 0:
                info = info + ' Number of contacts: %i Download detailed contact spreadsheet: %s/contact_csv/%d ' %(contacts, base_url, doc.id)

        return info

    def item_title(self, item):
        reg = find_regMD(item)
        doc = Document.objects.get(url=item.link)
        doc_type = doc.doc_type
        name = reg.reg_name
        title = "%s-- %s %s" %(name, doc_type, upload_date)
        return title


class RegionFeed(Feed):
   
    def get_object(self, request, region):
        self.link = "/region/" + region + "/rss"
        region = region.replace("__", "-").replace("_", " ").title()
        self.description = "Latest Foreign Agent Registration Act updates for all registrants that represent a client from %s. Includes a link to the source document, client list and summary information." % (region)
        self.title =  "Latest %s entries in the Foreign Influence Database" %(region)
        return Location.objects.filter(region=region)[0]

    def items(self, location):
        docs = Document.objects.filter(processed=True).order_by('-stamp_date')[:50]
        hits = []
        for d in docs:
            reg = find_reg(d)
            clients = reg.clients.all()
            if len(clients) > 0:
                for l in clients:
                    if l.location.region == location.region:    
                        if d not in hits:
                            hits.append(d)
        hits = hits[:20]
        return hits #document objects being returned
    
    def item_pubdate(self, item):
        return datetime.combine(item.stamp_date, datetime.min.time())
        
    def item_link(self, item):
        return item.url

    def item_guid(self, item):
         return item.url

    def item_description(self, item):
        info = "Date received: %s " %(item.stamp_date)
        link = item.url
        doc_type = item.doc_type
        reg = find_reg(item)

        client = ' '
        clients = reg.clients.all()
        for c in clients:
            client = client + c.client_name + "; "
        
        if len(client) > 0:
            info = info + "Active clients: %s"%(client)
        
        terminated = ' '
        terminated_clients = reg.terminated_clients.all()
        for c in terminated_clients:
            terminated = c.client_name + "; "
        
        if len(terminated) > 0:
            info = info + "Terminated clients: %s"%(terminated) 
        
        if doc_type == "Exhibit AB":
            try:
                new_client = ClientReg.objects.get(link=link)
                info = info + "New client: " + new_cient
            except:
                pass

        if doc_type == "Supplemental":
            pay_info = compute_pay(link)
            if pay_info != None:
                info = info + pay_info
            
            contacts = Contact.objects.filter(link=link).count()
            if contacts > 0:
                info = info + ' Number of contacts: %i Download detailed contact spreadsheet: %s/contact_csv/%d ' %(contacts, base_url, item.id)

        if doc_type == "Registration":
            pay_info = compute_pay(link)
            if pay_info != None:
                info = info + pay_info 

            contacts = Contact.objects.filter(link=link).count()
            if contacts > 0:
                info = info + ' Number of contacts: %i Download detailed contact spreadsheet: %s/contact_csv/%d ' %(contacts, base_url, item.id)

        return info

    def item_title(self, item):
        reg = find_reg(item)
        name = reg.reg_name
        title = "%s-- %s %s" %(name, item.doc_type, item.stamp_date)
        return title

class BigSpenderFeed(Feed):
    title = "Registrants that report over $1,000,000 in a reporting period."
    link = base_url + "/big_spender/rss/"
    description = "Foreign Agent Registrations that receive over $1,000,000 in a 6-month reporting period.  Includes a link to the source document, client list and summary information."

    def items(self):
        spenders = []
        docs = Document.objects.filter(processed=True,doc_type="Supplemental").order_by('-stamp_date')[:50]
        for d in docs:
            payment_count = Payment.objects.filter(link=d.url).count()
            if payment_count > 0:
                total = 0
                payments = Payment.objects.filter(link=d.url)
                for item in payments:
                    total += item.amount
                if total > 1000000:
                    spenders.append(d)

        return spenders
    
    def item_title(self, item):
        reg = find_reg(item)
        name = reg.reg_name
        title = "%s-- %s %s" %(name, item.doc_type, item.stamp_date)
        return title

    def item_pubdate(self, item):
        return datetime.combine(item.stamp_date, datetime.min.time())
        
    def item_link(self, item):
        return item.url

    def item_guid(self, item):
         return item.url

    def item_description(self, item):
        info = "Date received: %s " %(item.stamp_date)
        link = item.url
        doc_type = item.doc_type
        reg = find_reg(item)

        client = ' '
        clients = reg.clients.all()
        for c in clients:
            client = client + c.client_name + "; "
        
        if len(client) > 0:
            info = info + "Active clients: %s"%(client)
        
        terminated = ' '
        terminated_clients = reg.terminated_clients.all()
        for c in terminated_clients:
            terminated = c.client_name + "; "
        if len(terminated) > 0:
            info = info + "Terminated clients: %s"%(terminated)

        if doc_type == "Exhibit AB":
            try:
                new_client = ClientReg.objects.get(link=link)
                info = info + "New client: " + new_cient
            except:
                pass

        if doc_type == "Supplemental":
            pay_info = compute_pay(link)
            if pay_info != None:
                info = info + pay_info
            
            contacts = Contact.objects.filter(link=link).count()
            if contacts > 0:
                info = info + ' Number of contacts: %i Download detailed contact spreadsheet: %s/contact_csv/%d ' %(contacts, base_url, item.id)

        if doc_type == "Registration":
            pay_info = compute_pay(link)
            if pay_info != None:
                info = info + pay_info 

            contacts = Contact.objects.filter(link=link).count()
            if contacts > 0:
                info = info + ' Number of contacts: %i Download detailed contact spreadsheet: %s/contact_csv/%d ' %(contacts, base_url, item.id)

        return format_html(info)    

