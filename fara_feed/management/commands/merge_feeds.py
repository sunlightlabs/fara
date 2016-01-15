import scrapelib
import datetime

from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand, CommandError
from django.core.files.storage import default_storage
from django.conf import settings 

from FaraData.models import Historical, HistoricalDoc, MetaData, Registrant, Client, Location, ClientReg

head = ({'User-Agent': 'Mozilla/5.0'})


documents = []


class Command(BaseCommand):
    help = "Merges data from fara_feed and historical_feed."
    can_import_settings = True

    def handle(self, *args, **options):
        for doc in HistoricalDoc.objects.all():
            link = doc.document_link
            related_fara_metadata = MetaData.objects.filter(link=link)
            if len(related_fara_metadata) == 0:
                #skip for now
                #we may want to add the metadata
                continue


            #look for the registrant
            hist_reln = doc.historical_relationship
            registrant_no = hist_reln.registrant_no
            registrant = Registrant.objects.filter(reg_id=registrant_no)
            if len(registrant) == 1:
                registrant = registrant[0]
            elif len(registrant) == 0:
                registrant = Registrant(reg_id=registrant_no,
                                        reg_name=hist_reln.registrant)
                registrant.save()
            else:
                #there's more tha one registrant with the same ID
                #what should we do?
                print("Multiple registrants with that ID, moving on!")
                continue


            #look for the client
            names = create_search_names(hist_reln.principal)
            for name in names:
                clients = Client.objects.filter(client_name__iexact=name)
                if len(clients) > 0:
                    break

            if len(clients) == 1:
                client = clients[0]
            elif len(clients) > 1:
                #multiple matching clients, help! skipping for now
                print("Multiple clients with that name, moving on")
            else:
                location_text = hist_reln.location_represented

                #create the client
                #but first we have to match the location.

                #clean up known location mismatches
                location_dict = {'SOMALI DEMOCRATIC REPUBLIC' : 'SOMALIA',
                                'KOREA REPUBLIC OF' : 'SOUTH KOREA',
                                'BOSNIA-HERZEGOVINA' : 'BOSNIA AND HERZEGOVINA'}
                if location_text in location_dict:
                    location_text = location_dict[location_text]

                location = Location.objects.filter(location__iexact=location_text)
                if len(location) == 1:
                    location = location[0]
                else:
                    print "Unknown location {}".format(location_text)
                    continue
                client = Client(location=location,
                                client_name=name.strip(),
                                address1=hist_reln.address,
                                state=hist_reln.state)
                #only going to save client if it actually needs
                #to be added

            for md in related_fara_metadata:

                new_registrant = False

                #with registrants we can use their id system to dedup
                #so we'll just add them if they aren't in there

                if not registrant in md.registrant_set.all():
                    md.registrant_set.add(registrant)
                    md.save()
                    new_registrant = True            
                    registrant.meta_data.add(link)
                #for clients we have to be more careful since there's no id
                #so we'll only add clients if the client_set is empty
                #otherwise we may add duplicates
                #and presumably only human-entered data is in the db and it's good?
                if len(md.client_set.all()) == 0:
                    client.save() #we're good to save now
                    md.client_set.add(client)
                    md.save()
                    for r in md.registrant_set.all():
                        cr = ClientReg(client_id=client,
                                reg_id=r)
                        cr.save()
                        cr.meta_data.add(link)
                        cr.save()
                elif new_registrant:
                    for c in md.client_set.all():
                        cr = ClientReg(client_id=c,
                                reg_id=registrant)
                        cr.save()
                        cr.meta_data.add(link)
                        cr.save()






def create_search_names(name):
    name = name.strip()
    names = [name]
    #do any other name-related replacements here
    #eg:
    if "Saint" in name:
        names.append(name.replace("Saint","St"))
        names.append(name.replace("Saint","St."))

    return names
