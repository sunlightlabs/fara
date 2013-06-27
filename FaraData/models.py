import re

from django.db import models
from django.contrib import admin
from django.forms import ModelForm, Select


# the person, like a congressperson, that receives communication or contribution
class Recipient(models.Model):
    crp_id = models.CharField(max_length=7, null=True, blank=True)
    agency = models.CharField(max_length=100, blank=True, null=True)
    office_detail = models.CharField(max_length=100, blank=True, null=True)# formerly agency and office in agency detail
    name = models.CharField(max_length=150, null=True)
    title = models.CharField(max_length=300, null=True)  
    
    def __unicode__(self):
        return "%s %s of %s" %(self.title, self.name, self.agency) 

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
    country_grouping = models.CharField(max_length=200)
    region = models.CharField(max_length=200)

    def __unicode__(self):
        return self.location

#Questions 7, 8 and 9
class Client(models.Model):
    location = models.ForeignKey(Location)
    client_name = models.CharField(max_length=200, unique=True)
    address1 = models.CharField(max_length=300, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)#long to accommodate foreign addresses
    zip_code = models.CharField(max_length=50, null=True, blank=True) 
    #not using this right now but Bill mentioned he would like to do it in the future. 
    client_type = models.CharField(max_length=25, null=True, blank=True)
    
    def __unicode__(self):
        return self.client_name

# the firm or person doing the lobbying and registering with FARA (including those that represent themselves)       
class Registrant(models.Model):
    reg_id = models.IntegerField(primary_key=True) #this is assigned by DOJ
    reg_name = models.CharField(max_length=200, unique=True)
    address = models.CharField(max_length=300, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=2, null=True, blank=True)
    zip = models.CharField(max_length=10, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)# currently with clients
    terminated_clients = models.ManyToManyField(Client, related_name='terminated_clients', null=True, blank=True)
    clients = models.ManyToManyField(Client, null=True, blank=True)    
    lobbyists = models.ManyToManyField(Lobbyist, null=True, blank=True)
     
    def __unicode__(self):
        return self.reg_name

#Question 14(c)        
# new category
class Gift(models.Model):
    client = models.ManyToManyField(Client, null=True, blank=True)
    date = models.DateField(null=True, blank=True) 
    purpose = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    link = models.CharField(max_length=100)
    registrant = models.ForeignKey(Registrant)
    recipient = models.ForeignKey(Recipient, null=True, blank=True)
    
    def __unicode__(self):
        return "%s to %s" % (self.discription, self.registrant)
         
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
    date = models.DateField(null=True) 
    link = models.CharField(max_length=100)

    def __unicode__(self):
        return "%s - %s - %s" % (self.client, self.registrant, self.date )

#question 14 (a)
class Payment(models.Model):
    client = models.ForeignKey(Client)
    registrant = models.ForeignKey(Registrant)
    fee = models.BooleanField(default=False)# was feesretainer = models.CharField(max_length=1)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    purpose = models.TextField(null=True)
    date = models.DateField(null=True)
    link = models.CharField(max_length=100)
    
    def __unicode__(self):
         return "$%s from %s to %s" %(self.amount, self.client, self.registrant)

#question 15 (a)
class Disbursement(models.Model):
    client = models.ForeignKey(Client)
    registrant = models.ForeignKey(Registrant)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    purpose = models.TextField(null=True, blank=True)
    date = models.DateField(null=True)
    link = models.CharField(max_length=100) 
    subcontractor = models.ForeignKey(Registrant, related_name='subcontractor')
    
    def __unicode__(self):
        return "%s - %s - $%s" % (self.client, self.registrant, self.amount )

# this will probably phased out and replaced with IE info
#15 (c)
class Contribution(models.Model):
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    date = models.DateField(null=True, blank=True) 
    link = models.CharField(max_length=100)
    registrant = models.ForeignKey(Registrant)
    recipient = models.ForeignKey(Recipient)
    lobbyist = models.ForeignKey(Lobbyist, null=True, blank=True)# it should not be blank but I want it to be compatible with old data
    
    def __unicode__(self):
        return "%s - %s - $%s" % (self.recipient, self.registrant, self.amount )
    
class MetaData(models.Model):
    link = models.CharField(primary_key=True, max_length=255)
    upload_date = models.DateField(null=True)
    reviewed = models.BooleanField(default=False)
    processed = models.BooleanField(default=False)#processed means form is finished and info can be displayed on front end
    is_amendment = models.BooleanField(default=False)
    form = models.CharField(max_length=300)# I am guessing on this, we are storing on amazon
    notes = models.TextField(blank=True, null=True)
    
    def __unicode__(self):
        if len(str(self.notes)) < 1:
            return self.link
        else:
            return "%s (%s)" %(self.link, self.notes)

    
#models for the data entry form.
#would like to phase this one out
class RegForm(ModelForm):
    class Meta:
        model = Registrant
        exclude = ('terminated_clients', 'clients', 'lobbyists', 'description')

class RecipientForm(ModelForm):
    class Meta:
        model = Recipient

#also phasing out this one
class ClientForm(ModelForm):
    class Meta:
        model = Client

    