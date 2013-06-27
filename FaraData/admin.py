from django.contrib import admin

from FaraData.models import Registrant, Client, Recipient, Lobbyist, Gift, Contact, Payment, Disbursement, Contribution, MetaData, Location

class reg_admin(admin.ModelAdmin):
    search_fields=['reg_name', 'reg_id' ]
admin.site.register(Registrant, reg_admin)
    
class client_admin(admin.ModelAdmin):
    search_fields=['client_name']
admin.site.register(Client, client_admin) 

class recip_admin(admin.ModelAdmin):
    search_fields=['client_name']
admin.site.register(Recipient)

#this one look a but weird if you have time go back to it
class lobby_admin(admin.ModelAdmin):
    search_fields=['lobbyist_name', 'PAC_name']
admin.site.register(Lobbyist, lobby_admin)

class meta_admin(admin.ModelAdmin):
    search_fields=['link']
admin.site.register(MetaData, meta_admin)

#would be good to add reg but it doesn't work
class gift_admin(admin.ModelAdmin):
    search_fields=['discription', 'link']
admin.site.register(Gift, gift_admin)

class location_admin(admin.ModelAdmin):
    search_fields=['location', 'country_group']
admin.site.register(Location, location_admin)

#may want to add search to these later
admin.site.register(Contact)
admin.site.register(Payment)
admin.site.register(Disbursement)
admin.site.register(Contribution)


    