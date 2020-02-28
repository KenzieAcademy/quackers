import dotenv
import os
import slack
from airtable import Airtable
import json

dotenv.load_dotenv()
client = slack.WebClient(token=os.environ["BOT_USER_OAUTH_ACCESS_TOKEN"])

a = Airtable(os.environ.get('SE_AIRTABLE_BASE_ID'), 'Students')
# a = Airtable(os.environ.get('UX_AIRTABLE_BASE_ID'), 'Students')
students = a.get_all()

result = client.users_list()
users = [u for u in result.data['members'] if u['deleted'] is False]
processed_results = [
    [
        u['real_name'], u['profile']['display_name'], u['profile'].get('email'), u['id']
    ] for u in users
]

for record in students:
    student_email = record['fields'].get('Email')
    if record['fields'].get('Slack ID'):

        print("Record {record['fields']['Full Name']} is up to date!")
    if not student_email:
        continue
    for i in processed_results:
        if i[2]:
            i[2] = i[2].lower()
        if student_email.lower() == i[2]:
            try:
                # SE airtable
                print('Updating {}'.format(record['fields']['Full Name']))
            except KeyError:
                # UX airtable
                print('Updating {}'.format(record['fields']['Name']))
            a.update(record['id'], {'Slack ID': i[3]})
            i.append('PROCESSED')

unprocessed = [u for u in processed_results if len(u) == 4]
processed = [u for u in processed_results if len(u) == 5]
print("Unprocessed Slack IDs: ", len(unprocessed))
print("Number of students in Airtable: ", len(students))
print("Updated Slack IDs: ", len(processed))

students = a.get_all()
no_slack_id = [u for u in students if u['fields'].get('Slack ID') == None]
if len(no_slack_id) == 0:
    print(
        "Everyone present and accounted for! All student records in Airtable"
        " have a Slack ID."
    )
else:
    print("Found {} students in Airtable with no Slack ID.".format(len(no_slack_id)))
    print("This will require manual intervention.")
    print()
    print("Accounts that need attention:")
    for i in no_slack_id:
        try:
            print(i['fields']['Full Name'])
        except KeyError:
            print(i)

print()
print('The full unprocessed results from Slack are found in slack_data.json')

with open('slack_data.json', 'w') as f:
    data = {'data': []}
    [
        data['data'].append({
            'Real name': u[0],
            'Display name': u[1],
            'Email': u[2],
            'Slack ID': u[3]
        }) for u in unprocessed
    ]
    f.write(json.dumps(data, indent=2))
