import re

from django.db import models
from django.contrib import admin
from django.forms import ModelForm, Select


# the person, like a congressperson, that receives communication or contribution
class Recipient(models.Model):
    crp_id = models.CharField(max_length=9, null=True, blank=True)
    agency = models.CharField(max_length=100, blank=True, null=True)
    office_detail = models.CharField(max_length=100, blank=True, null=True)# formerly agency and office in agency detail
    name = models.CharField(max_length=150, null=True)
    title = models.CharField(max_length=300, null=True, blank=True)  
    # this would be for contributions to state or local candidates
    state_local = models.BooleanField(default=False)
    
    def __unicode__(self):
        if self.title != None:
            if self.agency != None:
                return "%s %s of %s" %(self.title, self.name, self.agency) 
            else:
                return "%s %s" %(self.title, self.name) 
        else: 
            if self.agency != None:
                return "%s of %s" %(self.name, self.agency) 
            else:
                return "%s" % (self.name) 


    def __str__(self):
        if self.title != None:
            if self.agency != None:
                return "%s %s of %s".encode('ascii', errors='ignore') % (self.title, self.name, self.agency)
            else:
                return "%s %s".encode('ascii', errors='ignore') % (self.title, self.name)
        else:
            if self.agency != None:
                return "%s of %s".encode('ascii', errors='ignore') % (self.name, self.agency)
            else:
                return "%s".encode('ascii', errors='ignore') % (self.name)


class Lobbyist(models.Model):
    lobby_id = models.CharField(max_length=150, null=True, blank=True)# this would be good for looking up contribs
    lobbyist_name = models.CharField(max_length=150, null=True, blank=True)
    PAC_name = models.CharField(max_length=150, null=True, blank=True)# this would be used for donations by PACs
    
    def __unicode__(self):
        name = str(self.lobbyist_name) + str(self.PAC_name)
        name = re.sub('None','', name)
        return "%s" %(name)

class Location(models.Model):
    location = models.CharField(max_length=200, unique=True)
    country_grouping = models.CharField(max_length=200, blank= True, null=True, default='')
    region = models.CharField(max_length=200, blank= True, null=True)

    def __unicode__(self):
        return self.location

#Questions 7, 8 and 9
class Client(models.Model):
    location = models.ForeignKey(Location)
    client_name = models.CharField(max_length=200)
    address1 = models.CharField(max_length=300, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)#long to accommodate foreign addresses
    zip_code = models.CharField(max_length=50, null=True, blank=True) 
    #These are for AB forms
    client_type = models.CharField(max_length=25, null=True, blank=True)
    # this will move to client reg
    description = models.TextField(null=True, blank=True)
    
    def __unicode__(self):
        return self.client_name

    def yearly_client_pay(self):
        client_totals = {}
        client_id = self.id
        payments = Payment.objects.filter(client=self)

        for p in payments:
            if client_contacts.has_key(client_id):
                if p.date == None:
                    meta = MetaData.objects.get(link=p.link)
                    p.date = meta.upload_date
                year = p.date.year
                
                if p.fee == True:
                    if client_totals[client_id].has_key('lobbying_total'):
                        if client_totals[client_id]['lobbying_total'].has_key(year):
                            client_totals[client_id]['lobbying_total'][year] += amount
                        else:
                            client_totals[client_id]['lobbying_total'][year] = amount
                    else:
                       client_totals[client_id]['lobbying_total'][year] = amount 

                    if client_totals[client_id].has_key('total'):
                        if client_totals[client_id]['total'](year):
                            client_totals[client_id]['total'][year] += amount
                        else:
                            client_totals[client_id]['total'][year] = amount
                    else:
                        client_totals[client_id]['total'][year] = amount
            else:
                if p.fee == True:
                    client_totals[client_id]['lobbying_total'][year] = amount
                client_totals[client_id]['total'][year] = amount

            return client_totals

    def yearly_client_contact(self):
        client_contacts = {}
        client_id = self.id
        contacts = Contact.objects.filter(client=self)

        for c in contacts:
            if c.date == None:
                meta = MetaData.objects.get(link=c.link)
                c.date = meta.upload_date
            year = c.date.year

            if client_contacts.has_key(client_id):
                contact_total[client_id] += 1
            else:
                contact_total[client_id] = 1

        return client_contacts
# the firm or person doing the lobbying and registering with FARA (including those that represent themselves)       
class Registrant(models.Model):
    reg_id = models.IntegerField(primary_key=True) #this is assigned by DOJ
    reg_name = models.CharField(max_length=200)
    address = models.CharField(max_length=300, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=2, null=True, blank=True)
    zip_code = models.CharField(max_length=10, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    terminated_clients = models.ManyToManyField(Client, related_name='terminated_clients', null=True, blank=True)
    clients = models.ManyToManyField(Client, null=True, blank=True)    
    lobbyists = models.ManyToManyField(Lobbyist, null=True, blank=True)
     
    def __unicode__(self):
        return self.reg_name

    # Payment aggregate 
    def yearly_reg_pay(self):
        reg_totals = {}
        reg_id = self.reg_id
        payments = Payment.objects.filter(registrant=self)
        
        for p in payments:
            if p.date == None:
                meta = MetaData.objects.get(link=p.link)
                p.date = meta.upload_date
            year = p.date.year
            
            if reg_totals.has_key(reg_id):
                if p.fee == True:
                    if reg_totals[reg_id].has_key('lobbying_total'):
                        if reg_totals[reg_id]['lobbying_total'].has_key(year):
                            reg_totals[reg_id]['lobbying_total'][year] += amount
                        else:
                            reg_totals[reg_id]['lobbying_total'][year] = amount
                    else:
                       reg_totals[reg_id]['lobbying_total'][year] = amount 

                    if reg_totals[reg_id].has_key('total'):
                        if reg_totals[reg_id]['total'](year):
                            reg_totals[reg_id]['total'][year] += amount
                        else:
                            reg_totals[reg_id]['total'][year] = amount
                    else:
                        reg_totals[reg_id]['total'][year] = amount
            else:
                if p.fee == True:
                    reg_totals[reg_id]['lobbying_total'][year] = amount
                reg_totals[reg_id]['total'][year] = amount

            return reg_totals

    # disbursement aggregate 
    def yearly_reg_dis(self):
        dis_totals = {}
        reg_id = self.reg_id
        disbursement = Disbursement.objects.filter(registrant=self)

        for d in disbursement:
            if d.date == None:
                meta = MetaData.objects.get(link=d.link)
                d.date = meta.upload_date
            year = d.date.year

            if dis_totals.has_key(reg_id):
                dis_totals[reg_id] += d.amount
            else:
                dis_totals[reg_id] = d.amount
        return dis_totals

    #counts the number of contact records per year
    def yearly_reg_contact(self):
        contact_total = {}
        reg_id = self.reg_id
        contact = Contact.objects.filter(registrant=self)

        for c in contact:
            if c.date == None:
                meta = MetaData.objects.get(link=c.link)
                c.date = meta.upload_date
            year = c.date.year
            client_id = c.client.id
            if contact_total.has_key(reg_id):
                contact_total[reg_id] += 1
            else:
                contact_total[reg_id] = 1

        return contact_total

#Question 14(c)        
# new category
class Gift(models.Model):
    client = models.ManyToManyField(Client, null=True, blank=True)
    date = models.DateField(null=True, blank=True) 
    purpose = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    link = models.CharField(max_length=100, db_index=True)
    registrant = models.ForeignKey(Registrant)
    recipient = models.ForeignKey(Recipient, null=True, blank=True)
    
    def __unicode__(self):
        return "%s to %s" % (self.description, self.registrant)
         
MEETING_TYPES = (
    ('P', 'Phone'),
    ('E', 'Email'),
    ('M', 'Meeting'),
    ('O', 'Other'),
    ('U', 'Unknown'))

#question 12
class Contact(models.Model):
    client = models.ForeignKey(Client, null=True)
    registrant = models.ForeignKey(Registrant)
    recipient = models.ManyToManyField(Recipient)
    contact_type = models.CharField(max_length=1, choices=MEETING_TYPES, default='U')
    description = models.TextField(blank=True, null=True) # issues on the old site
    lobbyist = models.ManyToManyField(Lobbyist, null=True, blank=True)
    date = models.DateField(null=True, blank=True) 
    link = models.CharField(max_length=100, db_index=True)

    def __unicode__(self):
        return "%s - %s - %s" % (self.client, self.registrant, self.date )

#question 14 (a)
class Payment(models.Model):
    client = models.ForeignKey(Client)
    registrant = models.ForeignKey(Registrant)
    fee = models.BooleanField(default=False)# was feesretainer = models.CharField(max_length=1)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    purpose = models.TextField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    link = models.CharField(max_length=100, db_index=True)
    subcontractor = models.ForeignKey(Registrant, related_name='payment_subcontractor', null=True, blank=True)
    
    def __unicode__(self):
         return "$%s from %s to %s" %(self.amount, self.client, self.registrant)

#question 15 (a)
class Disbursement(models.Model):
    client = models.ForeignKey(Client)
    registrant = models.ForeignKey(Registrant)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    purpose = models.TextField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    link = models.CharField(max_length=100, db_index=True) 
    #maybe this should only be with payment?
    subcontractor = models.ForeignKey(Registrant, related_name='subcontractor', null=True, blank=True)
    
    def __unicode__(self):
        return "%s - %s - $%s" % (self.client, self.registrant, self.amount )

# this will probably phased out and replaced with IE info
#15 (c)
class Contribution(models.Model):
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    date = models.DateField(null=True, blank=True) 
    link = models.CharField(max_length=100, db_index=True)
    registrant = models.ForeignKey(Registrant)
    recipient = models.ForeignKey(Recipient)
    lobbyist = models.ForeignKey(Lobbyist, null=True, blank=True)# it should not be blank but I want it to be compatible with old data
    
    def __unicode__(self):
        return "%s - %s - $%s" % (self.recipient, self.registrant, self.amount )

    def __str__(self):
        return "%s - %s - $%s".encode('ascii', errors='ignore') % (self.recipient, self.registrant, self.amount)
    
class MetaData(models.Model):
    link = models.CharField(primary_key=True, max_length=255, db_index=True)
    # similar to stamp date
    upload_date = models.DateField(null=True)
    reviewed = models.BooleanField(default=False)
    processed = models.BooleanField(default=False)#processed means form is finished and info can be displayed on front end
    is_amendment = models.BooleanField(default=False)
    form = models.CharField(max_length=300)# I am guessing on this, we are storing on amazon
    notes = models.TextField(blank=True, null=True)
    # this is just for supplementals
    end_date = models.DateField(null=True, blank=True)

    
    def __unicode__(self):
        if len(str(self.notes)) < 1:
            return self.link
        else:
            return "%s (%s)" %(self.link, self.notes)

#Thinking if this would simplify things for data entry, to keep track of subcontracting and find clients and registrants for particular forms.
#This will help create client based alerts on new clients
class ClientReg(models.Model):
    # one model for each client to registrant relationship
    client_id = models.ForeignKey(Client)
    reg_id = models.ForeignKey(Registrant)
    # if this client is coming from another contractor or contractors
    primary_contractor_id = models.ManyToManyField(Registrant, related_name='primary_contractor', null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    # this is the form where the information was last modified
    link = models.CharField(max_length=255, db_index=True)
    
    def __unicode__(self):
        return "%s - %s" % (self.client_id, self.reg_id)
    
#models for the data entry form.
class RegForm(ModelForm):
    class Meta:
        model = Registrant
        exclude = ('terminated_clients', 'clients', 'lobbyists', 'description')

class RecipientForm(ModelForm):
    class Meta:
        model = Recipient

class ClientForm(ModelForm):
    class Meta:
        model = Client

    