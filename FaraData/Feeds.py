from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

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

#@login_required(login_url='/admin')
class LatestEntriesFeed(Feed):
    title = "Latest entries in the Foreign lobbying database"
    link = "http://54.234.244.182/latest/rss/"
    description = "Updates"

    def items(self):
        return Document.objects.filter(processed=True).order_by('-stamp_date')[:25]

    def item_link(self, item):
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
        
        if len(client) > 1:
            info = info + "(Active clients: %s)"%(client)
        
        terminated = ' '
        terminated_clients = reg.terminated_clients.all()
        for c in terminated_clients:
            terminated = c.client_name + "; "
        if len(terminated) > 1:
            info = info + "(Terminated clients: %s)"%(terminated)

        if doc_type == "Exhibit AB":
            try:
                new_client = ClientReg.objects.get(link=link)
                info = info + "New client: " + new_cient
            except:
                pass

        if doc_type == "Supplemental":
            payments = Payment.objects.filter(link=link).count()
            contacts = Contact.objects.filter(link=link).count()
            if payments > 0:
                info = info + " Number of payments: %i Download payment spreadsheet: %s/payment_csv/%d" %(payments, base_url, item.id)
            if contacts > 0:
                info = info + " Number of contacts: %i Download contact spreadsheet: %s/contact_csv/%d" %(contacts, base_url, item.id)

        if doc_type == "Registration":
            payments = Payment.objects.filter(link=link).count()
            contacts = Contact.objects.filter(link=link).count()
            if payments > 0:
                info = info + " Number of payments: %i Download payment spreadsheet: %s/payment_csv/%d" %(payments, base_url, item.id)
            if contacts > 0:
                info = info + " Number of contacts: %i Download contact spreadsheet: %s/contact_csv/%d" %(contacts, base_url, item.id)

        return info

    def item_title(self, item):
        reg = find_reg(item)
        doc_type = item.doc_type
        name = reg.reg_name
        title = "%s-- %s %s" %(name, doc_type, upload_date)
        return title


class DataEntryFeed(Feed):
    title = "Latest entered documents in the Foreign lobbying database"
    link = "http://54.234.244.182/entry/rss/"
    description = "recently added"

    def items(self):
        return MetaData.objects.filter(processed=True).order_by('-upload_date')[:25]

    def item_link(self, item):
        return item.link

    def item_description(self, item):
        doc = Document.objects.get(url=item.link)
        doc_type = doc.doc_type
        info = "Date received: %s " %(doc.stamp_date)
        link = item.link
        reg = find_regMD(item)

        client = ' '
        clients = reg.clients.all()
        for c in clients:
            client + c.client_name
        if len(client) > 17:
            info = info + "(Active clients: %s)"%(client)
        
        terminated = ' '
        terminated_clients = reg.terminated_clients.all()
        for c in terminated_clients:
            terminated = c.client_name
        if len(terminated) > 20:
            info = info + "(Terminated clients: %s)"%(terminated)

        if doc_type == "Exhibit AB":
            try:
                new_client = ClientReg.objects.get(link=link)
                info = info + "New client: " + new_cient
            except:
                pass

        if doc_type == "Supplemental":
            payments = Payment.objects.filter(link=link).count()
            contacts = Contact.objects.filter(link=link).count()
            if payments > 0:
                info = info + " Number of payments: %i Download payment spreadsheet: %s/payment_csv/%d" %(payments, base_url, item.id)
            if contacts > 0:
                info = info + " Number of contacts: %i Download contact spreadsheet: %s/contact_csv/%d" %(contacts, base_url, doc.id)

        if doc_type == "Registration":
            payments = Payment.objects.filter(link=link).count()
            contacts = Contact.objects.filter(link=link).count()
            if payments > 0:
                info = info + " Number of payments: %i Download payment spreadsheet: %s/payment_csv/%d" %(payments, base_url, item.id)
            if contacts > 0:
                iinfo = info + " Number of contacts: %i Download contact spreadsheet: %s/contact_csv/%d" %(contacts, base_url, doc.id)

        return info

    def item_title(self, item):
        reg = find_regMD(item)
        doc = Document.objects.get(url=item.link)
        doc_type = doc.doc_type
        name = reg.reg_name
        title = "%s-- %s %s" %(name, doc_type, upload_date)
        return title

    def item_guid(self, item):
        client = ClientReg.objects.filter(link=self.link)
        return [client] 

class RegionFeed(Feed):
    title = "Latest entries in the Foreign lobbying database"
    description = "Updates"
    link = "placeholder"
   
    def get_object(self, request, region):
        region = region.replace("__", "-").replace("_", " ").title()
        return Location.objects.filter(region=region)[0]
        #case issue?

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
    
    def item_link(self, item):
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
        
        if len(client) > 1:
            info = info + "(Active clients: %s)"%(client)
        
        terminated = ' '
        terminated_clients = reg.terminated_clients.all()
        for c in terminated_clients:
            terminated = c.client_name + "; "
        if len(terminated) > 1:
            info = info + "(Terminated clients: %s)"%(terminated)

        if doc_type == "Exhibit AB":
            try:
                new_client = ClientReg.objects.get(link=link)
                info = info + "New client: " + new_cient
            except:
                pass

        if doc_type == "Supplemental":
            payments = Payment.objects.filter(link=link).count()
            contacts = Contact.objects.filter(link=link).count()
            if payments > 0:
                info = info + " Number of payments: %i Download payment spreadsheet: %s/payment_csv/%d" %(payments, base_url, item.id)
            if contacts > 0:
                info = info + " Number of contacts: %i Download contact spreadsheet: %s/contact_csv/%d" %(contacts, base_url, item.id)

        if doc_type == "Registration":
            payments = Payment.objects.filter(link=link).count()
            contacts = Contact.objects.filter(link=link).count()
            if payments > 0:
                info = info + " Number of payments: %i Download payment spreadsheet: %s/payment_csv/%d" %(payments, base_url, item.id)
            if contacts > 0:
                info = info + " Number of contacts: %i Download contact spreadsheet: %s/contact_csv/%d" %(contacts, base_url, item.id)

        return info

    def item_title(self, item):
        reg = find_reg(item)
        name = reg.reg_name
        title = "%s-- %s %s" %(name, item.doc_type, item.stamp_date)
        return title


