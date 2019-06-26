import requests
import time
from datetime import datetime, timedelta
import boto3

access_key = ''
secret_key = ''
slack_test_url = ''

def sessionManager(region):
    t = datetime.utcnow() - timedelta(seconds=65)
    t = t.strftime('%Y-%m-%d'+'T'+'%H:%M:%S'+'Z')
    
    ec2_ssm = boto3.client(
        'ssm',
        # Hard coded strings as credentials, not recommended.
        aws_access_key_id = access_key,
        aws_secret_access_key = secret_key,
        region_name = region
    )
    ec2_resource = boto3.resource(
        'ec2',
        # Hard coded strings as credentials, not recommended.
        aws_access_key_id = access_key,
        aws_secret_access_key = secret_key,
        region_name = region
    )    

    sessions = ec2_ssm.describe_sessions(
        State = 'Active',
        Filters = [
            {
                'key': 'InvokedAfter',
                'value': t
            },
            {
                'key': 'Status',
                'value': 'Connected'
            },
        ]
    )
    for i in sessions['Sessions']:
        # print(i['Owner'])
        # print(i['Target'])
        # print(i['StartDate'])

        instance = ec2_resource.Instance(i['Target'])
        tmp_ec2 = instance.tags
        env = ''
        name = ''
        for k in tmp_ec2:
            if k.get('Key') == 'Name':
                name = k.get('Value')            
            if k.get('Key') == 'system:Environment':
                env = k.get('Value')
                
        if env.lower() == 'prod':
            m = '*[AWS] EC2 Instance session manager*\n - user : {}\n - instance ID : {}\n - start time : {}'.format(i['Owner'], i['Target'], i['StartDate'])
            toSlack(m)
            
        
def toSlack(m):
    payload = {'text': m}
    requests.post(slack_test_url, json = payload)

if __name__ == '__main__':
    sessionManager('us-east-1')
    # sessionManager('ap-northeast-2')

        