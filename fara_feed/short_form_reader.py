import os
import re
import csv
from datetime import datetime


def clean_text(text):
    text = str(text)
    text = text.strip()
    return text

#gets info from files
def get_short_data(file_name):
    file = open(file_name)
    info = file.read()
    info = str(info)

    name = re.findall(r'1\.\ Name(.*?)2\.', info)
    for n in name:
        name =  clean_text(n)
    print name, ' new \n'

    sig_name = re.findall(r'\/s\/(.*?)eSigned', info)
    for sig in sig_name:
        sig_name = clean_text(sig)

    reg_id = file_name[12:16]
    reg_id = re.sub('-','', reg_id)
    reg_id = re.sub('S','', reg_id)

    person_id = re.findall(r'2. Registration No(.*?)Residence', info)
    person_id = clean_text(person_id)
    fara_lobby_id = ''
    for number in person_id:
        digit = re.findall(r'\d+', number)
        if len(digit) > 0:
            fara_lobby_id = fara_lobby_id + digit[0]

    short_data = [reg_id, name, sig_name, fara_lobby_id, file_name,]
    return short_data

#loops through files
def create_short_list():
    for file_tuple in os.walk(os.getcwd() + "/output_text"):
        files = file_tuple[2]
        short_list = []
        
        for f in files:
            file_name = "output_text/" + f
            print file_name
            short_data = get_short_data(file_name) 
            short_list.append(short_data)
    return short_list


short_list = create_short_list()
print short_list

# writes results to file
day = str(datetime.today())[:10]
csv_name = 'short_forms_' + day + '.csv'
writer = csv.writer(open(csv_name,'wb'))
labels = ['reg_id', 'name', 'sig_name', 'fara_lobby_id', 'file_name']
writer.writerow(labels)
for row in short_list:
    writer.writerow(row)



