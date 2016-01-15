import scrapelib
import datetime

from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand, CommandError
from django.core.files.storage import default_storage
from django.conf import settings 

from FaraData.models import Historical, HistoricalDoc

head = ({'User-Agent': 'Mozilla/5.0'})


documents = []


###Historical URLs look like this:
#https://efile.fara.gov/pls/apex/f?p=<p_flow_id>:<p_flow_step_id>:<p_instance>:<p_widget_action_mod>:<?>:<?>:<other parameter assignments?>
#where the params are separated by : and not named
#the only param we want to manipulate is <p_widget_action_mod>
#which needs to be in this format:
#pgR_min_row=1max_rows=15rows_fetched=15
#and max_rows and rows_fetched should say at 15
#because it always returns 15 anyway unless some other paramater
#I haven't yet figured out is changed.
#changing pgR_min_row modifies the starting point


#building the historical scraper completely separately
#from the regular fara feed scraper, and then a 
#task to combine them so that we always have the raw
#historical data and can combine when needed.

class Command(BaseCommand):
    help = "Crawls the DOJ's FARA site looking for new documents."
    can_import_settings = True

    def handle(self, *args, **options):
        self.scraper = scrapelib.Scraper()
        self.base_url = "https://efile.fara.gov/pls/apex/"
        self.per_page = 15 #right now we have no way of displaying
                            #anything but 15 at a time, this shouldn't
                            #be changed without a much better understanding
                            #of how they're passing parameters
        start_record = 0
        end_record = 0
        total_records = 1
        while end_record < total_records:
            page_param = "pgR_min_row={}max_rows={}rows_fetched={}"
            page_param = page_param.format(end_record+1, self.per_page, self.per_page)
            next_page = self.get_page(page_param)
            data_table = next_page.find('div', {'id' : 'apexir_DATA_PANEL'})
            self.process_records(data_table.findAll("tr"))
            page_info = next_page.find("td", { "class" : "pagination" }).text
            page_info = page_info.replace('of', '-')
            record_info = page_info.split('-')
            start_record, end_record, total_records = [int(r.strip()) for r in record_info]
            num_records_on_page = end_record-start_record+1

    def get_page(self, next_page_param):
        base_url = "https://efile.fara.gov/pls/apex/f?p=171:136:6066396580856:{}:NO::P136_CNTRY:ALL"
        page_url = base_url.format(next_page_param)
        page = self.scraper.get(page_url).text
        return BeautifulSoup(page)

    def get_docs(self, link, relationship_record):
        page = self.scraper.get(self.base_url+link).text
        soup = BeautifulSoup(page)
        try:
            soup.findAll('td', { "headers" : "DATE_STAMPED"})[0]
        except IndexError:
            #there are no records on this page, skip documents for this reln
            print "no records on %s" % self.base_url+link
            return []

        trs = soup.findAll('tr')
        for row in trs:
            date_stamped = row.find('td', {"headers":"DATE_STAMPED"})
            if date_stamped is None:
                #this was not a relevant TR
                continue

            date_stamped = clean_date_field(date_stamped)
            doc_link = row.find('td', {"headers":"DOCLINK"})
            doc_type = clean_field(row.find('td', {"headers":"DOCUMENT_TYPE"}))
            doc_name = clean_field(doc_link)
            doc_link = doc_link.a['href']

            if not doc_name:
                #there is no document pdf
                continue
            if doc_name.lower() != relationship_record.principal.lower():
                continue

            existing_docs = HistoricalDoc.objects.filter(document_link=doc_link,
                historical_relationship=relationship_record)
            
            if len(existing_docs) == 0:
                print "%s saved" % doc_link
                doc = HistoricalDoc(historical_relationship=relationship_record,
                                    document_type=doc_type,
                                    document_link=doc_link,
                                    document_name=doc_name,
                                    document_date=date_stamped)
                doc.save()





    def process_records(self, records):
        #find document's info
        country = None
        for record in records:
            if record.th:
                country_span = record.th.find('span', { "class" : "apex_break_headers" })
                if country_span:
                    country = country_span.text.strip()
            
            principal = record.find('td',{"headers": "FP_NAME BREAK_COUNTRY_NAME_1"})
            if principal:
                principal = principal.text.strip()
            if not principal:
                continue
            if not country:
                print "don't know which country, skipping"
                continue
            fp_reg_date = clean_date_field(record.find('td',{"headers": "FP_REG_DATE BREAK_COUNTRY_NAME_1"}))
            fp_term_date = clean_date_field(record.find('td',{"headers": "TERMINATION_DATE BREAK_COUNTRY_NAME_1"}))
            address = clean_field(record.find('td',{"headers": "ADDRESS_1 BREAK_COUNTRY_NAME_1"}))
            state = clean_field(record.find('td',{"headers": "STATE BREAK_COUNTRY_NAME_1"}))
            reg_name = clean_field(record.find('td',{"headers": "REGISTRANT_NAME BREAK_COUNTRY_NAME_1"}))
            reg_num = clean_field(record.find('td',{"headers": "REG_NUMBER BREAK_COUNTRY_NAME_1"}))
            reg_reg_date = clean_date_field(record.find('td',{"headers": "REG_DATE BREAK_COUNTRY_NAME_1"}))
            reg_term_date = clean_date_field(record.find('td',{"headers": "REG_TERM_DATE BREAK_COUNTRY_NAME_1"}))

            doc_page_link = record.find('td',{"headers": "LINK BREAK_COUNTRY_NAME_1"}).a["href"]

            #same principal and registrant with same reg dates for both
            #should be enough to determine uniqueness (I hope)
            obj_count = Historical.objects.filter(principal=principal,
                                        registrant=reg_name,
                                        principal_reg_date=fp_reg_date,
                                        registrant_reg_date=reg_reg_date).all()

            if len(obj_count) > 0:
                hist = obj_count[0]

            else:
                hist = Historical(principal=principal,
                    principal_reg_date = fp_reg_date,
                    principal_termination_date = fp_term_date,
                    address = address,
                    state = state,
                    location_represented = country,
                    registrant = reg_name,
                    registrant_no = reg_num,
                    registrant_reg_date = reg_reg_date,
                    registrant_termination_date = reg_term_date)

                

                hist.save()


            self.get_docs(doc_page_link, hist)


def clean_field(field):
    if field:
        field = field.text.strip()
    if field:
        return field
    return None

def clean_date_field(date):
    date = clean_field(date)
    if date:
        return datetime.datetime.strptime(date, '%m/%d/%Y')
    return None

      


