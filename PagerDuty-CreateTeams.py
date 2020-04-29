import requests
import json
from json import loads
import csv
import os.path

# The 'data/pdteams.csv' file contains a list of teams to be loaded in a Pager Duty account
# with the current structure of the record: <name>, <description>
# Upon a successful creation of a record in Pager Duty account, the returned user ID is appended to the
# corresponding record of the csv file, making the record structure as:<name>, <email>, <role>, <id>
# The use a csv file having an id on the fourth position of any of the records,
# will result in updating those user records into the Pager Duty account
my_path = os.path.abspath(os.path.dirname(__file__))
path = os.path.join(my_path, "data/pdteams.csv")


# Want to generate REST or Events API keys?
# Check here: https://support.pagerduty.com/docs/generating-api-keys
# Replace it with a valid PD access key
#PDAccountAccessKey = '***************jds2K'
PDAccountAccessKey ='SwEYWx-i3x24JMZhThxt'

# Update to match your PagerDuty email address
PD_ACCT_OWNER_EMAIL = 'cristian.i.balan@icloud.com'

def create_teams_from_csv():
    new_file_lines = []
    currentcreaterow=None
    try:
        with open(path, mode='r') as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            for row in readCSV:
                currentcreaterow=row
                teamid=create_team(row)
                currentcreaterow.append(teamid)
                print('row: ', currentcreaterow)
                new_file_lines.append(currentcreaterow)
                currentcreaterow = None
        with open(path, mode='w') as newcsvfile:
            writeCSV = csv.writer(newcsvfile, delimiter=',')
            writeCSV.writerows(new_file_lines)
    except FileNotFoundError:
        print("Cannot open {} file.".format(path))
    except :
        print ("Other exception/error has been encountered")

def create_team(list):
    url = 'https://api.pagerduty.com/teams'
    headers = {
        'Accept': 'application/vnd.pagerduty+json;version=2',
        'Authorization': 'Token token={token}'.format(token=PDAccountAccessKey),
        'Content-type': 'application/json',
        'From': PD_ACCT_OWNER_EMAIL
    }
    payload = {
        'team': {
            'type': 'team',
            'name': list[0],
            'description': list[1]
        }
    }
    try:
        r = requests.post(url, headers=headers, data=json.dumps(payload))
        print('Status Code: {code}'.format(code=r.status_code))
        print(r.json())
        return r.json()['team']['id']
    except:
        print ("Error processing the create_team's POST request")



if __name__ == '__main__':
    create_teams_from_csv()