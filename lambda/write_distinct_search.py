from __future__ import print_function

import json
import boto3

print('Loading function')

def lambda_handler(event, context):
    # print("Received event: " + json.dumps(event, indent=2))
    for record in event['Records']:
        print(record['eventID'])
        print(record['eventName'])
        print("DynamoDB Record: " + json.dumps(record['dynamodb'], indent=2))

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('distinct_follow_search')
        table.put_item(
            Item={
                'search': json.dumps(record['dynamodb']['Keys']['search']['S']).strip('\"')
            }
        )

    return 'Successfully processed {} records.'.format(len(event['Records']))
