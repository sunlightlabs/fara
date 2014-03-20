from datetime import datetime, date
import re

from django.core.management.base import BaseCommand, CommandError

from FaraData import spread_sheets
from FaraData.models import MetaData, Payment, Disbursement, Contact, Contribution, Registrant, Client, Gift
from fara_feed.models import Document
from fara_feed.management.commands.create_feed import add_document, add_file, save_text

class Command(BaseCommand):
    help = "Giant Influence Explorer downloads"
    can_import_settings = True
        
    def handle(self, *args, **options):
        pay_disburse_contact_contrib()
        add_reg()
    

def pay_disburse_contact_contrib():
    for payment in Payment.objects.all():
        link = payment.link
        if MetaData.objects.filter(link=link).exists():
            md = MetaData.objects.get(link=link)
        else:
            md = add_md(link)   
        payment.meta_data = md
        payment.save()
    
    print "done with payments"

    for disbursement in Disbursement.objects.all():
        link = disbursement.link
        if MetaData.objects.filter(link=link).exists():
            md = MetaData.objects.get(link=link)
        else:
            md = add_md(link)
        
        disbursement.meta_data = md 
        disbursement.save()
    
    print "done with disbursements"

    for contact in Contact.objects.all():
        link = contact.link
        if MetaData.objects.filter(link=link).exists():
            md = MetaData.objects.get(link=link)
        else:
            md = add_md(link)
        
        contact.meta_data = md
        contact.save()
    
    print "done with contacts"

    for contribution in Contribution.objects.all():
        link = contribution.link
        if MetaData.objects.filter(link=link).exists():
            md = MetaData.objects.get(link=link)
        else:
            md = add_md(link)
        
        contribution.meta_data = md
        contribution.save()

    print "done with contributions"

    for gift in Gift.objects.all():
        link = gift.link
        if MetaData.objects.filter(link=link).exists():
            md = MetaData.objects.get(link=link)
        else:
            md = add_md(link)  

        gift.meta_data = md
        gift.save()


def add_md(link):
    if Document.objects.filter(url=link).exists():
        doc = Document.objects.get(url=link)
    else:
        doc = add_doc(link)

    form = doc.id
    processed = doc.processed

    metadata= MetaData(link = link,
            upload_date =  date.today(),
            processed = processed,
            form = form,
            notes = "Legacy data",
    )
    metadata.save()
    print "Saving Metadata", metadata
    return metadata


def add_doc(link):
    print link, "NOT FOUND in documents"
    url = link
    stamp_date = re.findall(r'\d{8}', url)
    stamp_date = stamp_date[0]
    stamp_date_obj = datetime.strptime(stamp_date, "%Y%m%d")
    date_string = stamp_date_obj.strftime('%Y-%m-%d')
    reg_name = None

    reg_id = re.sub('-','', url[25:29])
    reg_id = re.sub('S','', reg_id)
    reg_id = re.sub('L','', reg_id)

    info = re.findall( r'-(.*?)-', url)

    if info[0] == 'Amendment':
        doc_type = 'Amendment'

    elif info[0] == 'Short':
        doc_type = 'Short Form'

    elif info[0] == 'Exhibit':
        if "AB" in url:
            doc_type = 'Exhibit AB'  
        if "C" in url:
            doc_type = 'Exhibit C'    
        if "D" in url:
            doc_type = 'Exhibit D'

    elif info[0] == 'Conflict':
        doc_type = 'Conflict Provision'

    elif info[0] == 'Registration':
        doc_type = 'Registration'

    elif info[0] == 'Supplemental':
        doc_type = 'Supplemental' 

    url_info= {'url':url,'reg_name':reg_name,  'reg_id':reg_id, 'doc_type':doc_type, 'stamp_date':date_string}
           
    add_document(url_info)
    add_file(url)
    save_text(url, url_info, outdir)

    return Document.objects.get(url=url)

def add_reg():
    for md in MetaData.objects.all():
        link = md.link
        reg_id = re.sub('-','', link[25:29])
        reg_id = re.sub('S','', reg_id)
        reg_id = re.sub('L','', reg_id)
        reg_id = int(reg_id)
        try:
            reg = Registrant.objects.get(reg_id=reg_id)
            reg.meta_data.add()
            reg.save()
        except:
            print "REG ERROR  ---- ", reg_id
        






