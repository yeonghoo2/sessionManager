import requests
import time
from datetime import datetime, timedelta
import boto3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

access_key = ''
secret_key = ''

def sessionManagerReport(region):
    data = []
    et = datetime.utcnow()
    et = et.strftime('%Y-%m-%d'+'T'+'00:00:00'+'Z')
    et_t = et.strftime('%Y-%m-%d')
    st = datetime.utcnow() - timedelta(days=7)
    st = st.strftime('%Y-%m-%d'+'T'+'00:00:00'+'Z')
    st_t = st.strftime('%Y-%m-%d')
    
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
        State = 'History',
        Filters = [
            {
                'key': 'InvokedAfter',
                'value': st
            },
            {
                'key': 'InvokedBefore',
                'value': et
            },
        ]
    )
    for i in sessions['Sessions']:
        # print(i['Owner'])
        # print(i['Target'])
        # print(i['StartDate'])
        try: # for scale in EC2
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
                owner = i['Owner'].split('/')[1]
                data.append([str(i['StartDate']), owner, i['Target'], name])
        except:
            continue

    df = pd.DataFrame(data, columns = ['time', 'user', 'instance id', 'instance name'])
    df['time'] = df['time'].apply(lambda x: x.split(':', 2)[0]+':00:00')
    sns.relplot(x="user", y="time", data=df, height=6, aspect=2, kind="scatter")
    
    plt.xticks(rotation=50)
    plt.title('{0} ~ {1}'.format(st_t, et_t), size = 25)
    # plt.show()
    plt.tight_layout()
    plt.savefig('./tmp.png', dpi=160)
    toSlackImage(region)
    
    """
    tmp = []
    for i in data:
        tmp.append(1)

    df2 = df
    df2['c'] = tmp
    del df2['instance id']
    del df2['instance name']
    
    df2 = df2.drop_duplicates()
    
    data_df2 = df2.pivot('time', 'user', 'c')
    display_df2 = sns.heatmap(data_df2, vmin=0, vmax=1, cmap="BuPu", linewidth=.5)
    plt.xticks(rotation=50)
    plt.title("Prod instance session manager", size = 25)
    plt.show()
    
    # http://seaborn.pydata.org/
    
    """

def toSlackImage(region):
    my_file = {
      'file' : ('./tmp.png', open('./tmp.png', 'rb'), 'png')
    }
    
    payload = {
        'token': '',
        'channels': 'webhook-test',
        'filename': 'tmp.png',
        'title': region + ' Session Manager Weekly Report'
    }
    
    r = requests.post('https://slack.com/api/files.upload', params=payload, files=my_file)
    
if __name__ == '__main__':
    sessionManagerReport('us-east-1')
    sessionManagerReport('ap-northeast-2')

        