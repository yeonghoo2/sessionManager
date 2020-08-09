import requests
import time
from datetime import datetime, timedelta
import boto3
import json

url = ""
slack_test_url = '' # martin channel

chk_time = datetime.utcnow() - timedelta(seconds=60.1)
chk_time = chk_time.strftime('%Y-%m-%d'+'T'+'%H:%M:%S'+'Z')

def get_ec2_env(ec2, ec2_object):
    instance = ec2_object.Instance(ec2)
    return [k.get('Value').lower() for k in instance.tags if k.get('Key') == 'system:Environment']

def get_ec2_name(ec2, ec2_object):
    instance = ec2_object.Instance(ec2)
    return [k.get('Value').lower() for k in instance.tags if k.get('Key') == 'Name']

def session_manager(region, state):
    ec2_ssm = boto3.client(
        'ssm',
        region_name = region
    )
    ec2_resource = boto3.resource(
        'ec2',
        region_name = region
    )

    sessions = ec2_ssm.describe_sessions(
        State = state,
        Filters = [
            {
                'key': 'InvokedAfter',
                'value': chk_time
            },
        ]
    )
    session_info = [[i['Owner'], i['SessionId'], i['Target'], i['StartDate'], get_ec2_name(i['Target'], ec2_resource)[0]] for i in sessions['Sessions'] if get_ec2_env(i['Target'], ec2_resource) == ['dev']]

    for i in session_info:
        message = f"*[AWS] EC2 Instance session manager*\n - role : {i[0]}\n - user : {i[1]}\n - instance name : {i[4]}\n - instance id : {i[2]}\n - start time : {i[3]}"
        # print(message)
        to_slack(message, slack_test_url)
            
def to_slack(m, url):
    headers = {'Content-Type': 'application/json; charset=utf-8'}
    data = {
        "channel": "ssh-logins",
        "username": "ssh-bot",
        "text" : m
    }
    requests.post(url, headers=headers, data=json.dumps(data))

region = ['ap-northeast-2', 'us-east-1', 'ap-northeast-2', 'us-east-1']
state = ['Active', 'History', 'History', 'Active']
list(map(session_manager, region, state))

        