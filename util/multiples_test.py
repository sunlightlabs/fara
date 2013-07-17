import json
import csv

from sys import path

json_data = open('fara.json')
data = json.load(json_data)

comma_list = []
maybe_member = []
multiple_flag = []

for line in data:
	if line['model'] == "fara.contact":
		if line['fields']['approved'] == 1:
			name = str(line['fields']['contact_name'])
			if name != None:
				if ',' in name:
					comma_list.append([name])
				else:
					print "this works"
				if ')' in name and line['fields']['contact_level'] != "Member":
					maybe_member.append([name, line['pk']])

			new_name = str(line['fields']['contact_name_new'])
			
			if name == None or name == '':
				name = new_name
			# some times name is rewritten last, first so I am ignoring those
			if len(new_name) > len(name) + 4:
				multiple_flag.append([name, new_name, crp_id])

writer = csv.writer(open('Multiples.csv','wb'))
for k in comma_list:	
		writer.writerow(k)	

writer = csv.writer(open('maybe_member.csv','wb'))
for k in maybe_member:	
		writer.writerow(k)

writer = csv.writer(open('multiple_flag.csv','wb'))
for k in multiple_flag:	
		writer.writerow(k)

json_data.close()
