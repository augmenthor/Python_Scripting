import requests
import json
from json import loads
import csv
import os.path

# The 'data/pdusers.csv' file contains a list of 50 records of fictitious users to be loaded in a Pager Duty account
# with the current structure of the record: <name>, <email>, <role>
# Upon a successful creation of a record in Pager Duty account, the returned user ID is appended to the
# corresponding record of the csv file, making the record structure as:<name>, <email>, <role>, <id>
# The use a csv file having an id on the fourth position of any of the records,
# will result in updating those user records into the Pager Duty account
my_path = os.path.abspath(os.path.dirname(__file__))
path = os.path.join(my_path, "data/pdusers.csv")
print (path)

# Want to generate REST or Events API keys?
# Check here: https://support.pagerduty.com/docs/generating-api-keys
#PDAccountAccessKey = '***************jds2K'
PDAccountAccessKey = '5689dh3Ak8VkSq-jds2K'

# Update to match your PagerDuty email address
PD_ACCT_OWNER_EMAIL = 'cristian.balan@augmenthor.com'

def create_or_update_users_from_csv():
    new_file_lines = []
    currentcreaterow=None
    try:
        with open(path, mode='r') as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            for row in readCSV:
                if len(row)==3:
                    currentcreaterow=row
                    userid=create_user(row)
                    currentcreaterow.append(userid)
                    print('row: ', currentcreaterow)
                    new_file_lines.append(currentcreaterow)
                    currentcreaterow = None
                elif len(row)>=3:
                    new_file_lines.append(row)
                    update_user(row)
        with open(path, mode='w') as newcsvfile:
            writeCSV = csv.writer(newcsvfile, delimiter=',')
            writeCSV.writerows(new_file_lines)
    except FileNotFoundError:
        print("Cannot open {} file.".format(path))
    except :
        print ("Other exception/error has been encountered")

def create_user(list):
    url = 'https://api.pagerduty.com/users'
    headers = {
        'Accept': 'application/vnd.pagerduty+json;version=2',
        'Authorization': 'Token token={token}'.format(token=PDAccountAccessKey),
        'Content-type': 'application/json',
        'From': PD_ACCT_OWNER_EMAIL
    }
    payload = {
        'user': {
            'type': 'user',
            'name': list[0],
            'email': list[1],
            'role': list[2]
        }
    }
    try:
        r = requests.post(url, headers=headers, data=json.dumps(payload))
        print('Status Code: {code}'.format(code=r.status_code))
        print(r.json())
        return r.json()['user']['id']
    except:
        print ("Error processing the creaate_user's POST request")


def update_user(list):
    url = 'https://api.pagerduty.com/users/{id}'.format(id=list[len(list)-1])
    headers = {
        'Accept': 'application/vnd.pagerduty+json;version=2',
        'Authorization': 'Token token={token}'.format(token=PDAccountAccessKey),
        'Content-type': 'application/json'
    }
    print(headers)
    payload = {
        'user': {
            'name': list[0],
            'email': list[1],
            'role': list[2]
        }
    }
    try:
        r = requests.put(url, headers=headers, data=json.dumps(payload))
        print('Status Code: {code}'.format(code=r.status_code))
        print(r.json())
    except:
        print ("Error processing the creaate_user's PUT request")


if __name__ == '__main__':
    create_or_update_users_from_csv()

