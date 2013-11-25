from FaraData.models import *
from fara_feed.models import *

def add_element(element):
	objects = element.objects.all()
	for o in objects:
		link = str(o.link)
		if link[24:36] == "/to_reimport":
			link= link[36:-4]
			link = "http://www.fara.gov/docs" + link + ".pdf"
			print link
			o.link = link
			o.save()

		elif link[:24] == "download_cache/processed":
			link = link[25:-4]
			link = "http://www.fara.gov/docs/" + link + ".pdf"
			print link
			o.link = link
			o.save()

		elif link[:8] == 'download':
			link = link[15:-4]
			link = "http://www.fara.gov/docs/" + link + ".pdf"
			print link
			o.link = link
			o.save()

add_element(Contact)
add_element(Payment)
add_element(Disbursement)
add_element(Contribution)

all_docs = Document.objects.all()
for o in all_docs:
	link = o.url
	if link[:4] != "http":
		bad_link = link
		if link[24:36] == "/to_reimport":
			link = link[36:-4]
			link = "http://www.fara.gov/docs" + link + ".pdf"
			print link
			o.url = link

		elif link[:24] == "download_cache/processed":
			link = link[25:-4]
			link = "http://www.fara.gov/docs/" + link + ".pdf"
			print link
			o.url = link

		elif link[:8] == 'download':
			link = link[15:-4]
			link = "http://www.fara.gov/docs/" + link + ".pdf"
			print link
			o.url = link
		
		if Document.objects.filter(url=link).exists:
			print "dupe"
			o.delete()
		else:
			doc = Document.objects.get(url=bad_link)
			doc.url = link
			doc.save()
			print "\nreplace\n"
