import boto3
import requests
import json

# Update to match a locally stored AWS profile
session = boto3.session.Session(profile_name='augmenthor')

PDAccountAccessKey ='SwEYWx-i3x24JMZhThxt'
# Update to match your PagerDuty email address
PD_ACCT_OWNER_EMAIL = 'cristian.i.balan@icloud.com'

sns_clnt = session.client('sns')
sns_topic_arn =None

sns_subscription_pd_protocol = 'HTTPS'
sns_subscription_arn =None

def create_escalation_policy(team_id):
    url = 'https://api.pagerduty.com/escalation_policies'
    headers = {
        'Accept': 'application/vnd.pagerduty+json;version=2',
        'Authorization': 'Token token={token}'.format(token=PDAccountAccessKey),
        'Content-type': 'application/json',
        'From': PD_ACCT_OWNER_EMAIL
    }
    payload = {
    "escalation_policy": {
        "type": "escalation_policy",
        "name": "DevOpsAPI",
        "escalation_rules": [
            {
                "escalation_delay_in_minutes": 30,
                "targets": [
                    {
                        "id": "PCHN6LF",
                            "type": "user_reference",
                            "summary": "Ionel Balan",
                            "self": "https://api.pagerduty.com/users/PCHN6LF",
                            "html_url": "https://cbalan.pagerduty.com/users/PCHN6LF"
                    }
                ]
            }
        ],
        "num_loops": 0,
        "on_call_handoff_notifications": "if_has_services",
        "teams": [
            {
                "id": "{teamid}".format(teamid=team_id),
                "type": "team_reference",
                "summary": "ACME Hotel Back Office - DevOps",
                "self": "https://api.pagerduty.com/teams/PJKUNJK",
                "html_url": "https://cbalan.pagerduty.com/teams/PJKUNJK"
            }
        ],
        "description": "Here is the ep for the devops team."
    }
}
    try:
        r = requests.post(url, headers=headers, data=json.dumps(payload))
        print('Status Code: {code}'.format(code=r.status_code))
        print('escalation ploicy id: '+ r.json()['escalation_policy']['id'])
        return r.json()['escalation_policy']['id']
    except:
        print ("Error processing the create_escalation_policy's POST request")

def create_service(escalation_policy_id):
    url = 'https://api.pagerduty.com/services'
    headers = {
        'Accept': 'application/vnd.pagerduty+json;version=2',
        'Authorization': 'Token token={token}'.format(token=PDAccountAccessKey),
        'Content-type': 'application/json',
        'From': PD_ACCT_OWNER_EMAIL
    }
    payload = {
    "service": {
        "type": "service",
        "name": "AWS CloudWatch API",
        "description": "AWS CloudWatch service (created via API)",
        "status": "active",
        "escalation_policy": {
            "id": escalation_policy_id,
            "type": "escalation_policy_reference"
        },
        "incident_urgency_rule": {
            "type": "constant",
            "urgency": "high"
        },
        "alert_creation": "create_alerts_and_incidents"
    }
}
    try:
        r = requests.post(url, headers=headers, data=json.dumps(payload))
        print('Status Code: {code}'.format(code=r.status_code))
        print('service id: '+r.json()['service']['id'])
        return r.json()['service']['id']
    except:
        print ("Error processing the create_service's POST request")

def create_integration(service_id, subdomain):
    url = 'https://api.pagerduty.com/services/{id}/integrations'.format(id=service_id)
    headers = {
        'Accept': 'application/vnd.pagerduty+json;version=2',
        'Authorization': 'Token token={token}'.format(token=PDAccountAccessKey),
        'Content-type': 'application/json',
        'From': PD_ACCT_OWNER_EMAIL
    }
    payload = {
        "integration": {
            "type": "event_transformer_api_inbound_integration",
            "name": "Amazon CloudWatch API",
            "service": {
                "id": service_id,
                "type": "service_reference",
                "summary": "Amazon CloudWatch API",
                "self": "https://api.pagerduty.com/services/{id}".format(id=service_id),
                "html_url": "https://{sd}.pagerduty.com/services/{id}".format(sd=subdomain,id=service_id)
            },
            "vendor": {
              "id": "PZQ6AUS",
              "type": "vendor_reference"
            }
        }
    }
    try:
        r = requests.post(url, headers=headers, data=json.dumps(payload))
        print('Status Code: {code}'.format(code=r.status_code))
        print('integration key: '+r.json()['integration']['integration_key'])
        return r.json()['integration']['integration_key']
    except Exception as error:
        print(error)

def create_sns_topic(topicname):
    # create an SNS topic
    try:
        response = sns_clnt.create_topic(Name=topicname)
        return response['TopicArn']
    except Exception as error:
        print(error)


def create_sns_subcription_endpoint(snstopicarn):
    # Subcribe to a PD endpoint (previously created in PD's admin console)
    try:
        response = sns_clnt.subscribe(
            TopicArn=snstopicarn,
            Protocol=sns_subscription_pd_protocol,
            Endpoint=sns_subscription_pd_endpoint,
            ReturnSubscriptionArn=True
        )
        return response['SubscriptionArn']
    except Exception as error:
        print(error)


if __name__ == '__main__':

    #create in PagerDuty sbdomain:
    # - an escalation policy for a single team, a new service
    # - a new service which will create alerts and incidents
    # - a new integration with AWS CloudWatch for the service created
    ep_team_id="PX7BN8L"
    service_subdomain="cbalan"
    ik=create_integration(create_service(create_escalation_policy(ep_team_id)), service_subdomain)

    #use the integration key to create an AWS SNS topic and subscription
    sns_subscription_pd_endpoint = "https://events.pagerduty.com/integration/{integration_key}/enqueue".format(
        integration_key=ik)
    #CloudWatch to pagerDuty Topic and Subscription creation
    sns_topic_arn=create_sns_topic("CloudWatch-to-PagerDuty")
    print("sns_topic_arn: {}".format(sns_topic_arn))
    sns_subscription_arn= create_sns_subcription_endpoint(sns_topic_arn)
    print("sns_subscription_arn: {}".format(sns_subscription_arn))
