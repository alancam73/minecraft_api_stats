# Periodically checks status, # players etc of a Minecraft server & pushes result
# to a DynamoDB table for later querying or visualization
# Leverages the Minecraft server API : https://api.mcsrvstat.us/

import boto3
import os
import urllib3
import json
from datetime import datetime

ec2 = boto3.client('ec2')

def lambda_handler(event, context):
    
    instance = []
    instance.append(str(os.environ['inst_name']))
    
    try: 
        response = ec2.describe_instance_status(InstanceIds=instance)
    
        # only proceed if the instance is RUNNING
        if response['InstanceStatuses'][0]['InstanceState']['Name'] == 'running':
            print('Instance ' + str(instance) + ' is running in Region : ' + ec2._client_config.region_name)
            
            # now check the status of the Minecraft Server
            http = urllib3.PoolManager()
            srv_name = str(os.environ['mcsrv_name'])
            r = http.request('GET', srv_name)
            svr_stat = json.loads(r.data.decode('utf-8'))
            print('Stats: ', svr_stat["ip"], svr_stat["online"], svr_stat["players"], svr_stat["version"])
            
            # use current date time as the primary partition key for the DynamoDB table
            curr_time = datetime.now()
            fmt_curr_time = curr_time.strftime("%Y-%m-%d %H:%M:%S")
            print('Current datetime:', fmt_curr_time)
        
            # now push the current minecraft API stats to DynamoDB
            tbl_resp = put_mcraft_stats(fmt_curr_time, svr_stat["online"], svr_stat["players"], svr_stat["version"])
            print('DynamoDB HTTP Status code:', tbl_resp['ResponseMetadata']['HTTPStatusCode'])
    
    except Exception as e:
        print('Instance ', str(instance), 'is not running')
        print(e)
        

def put_mcraft_stats(curr_time, online, players, version, dynamodb=None):
    
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb')

    tbl_name = str(os.environ['dynamodb_tbl']) 

    tbl = dynamodb.Table(tbl_name)
    response = tbl.put_item(
        Item={
            'date_time': curr_time,              # primary key (required)
            'p_online': online,                  # is Minecraft server on or offline
            'p_players': players,                # JSON blob of player details
            'p_version': version                 # Minecraft version number
        }
    )
    
    return response

    