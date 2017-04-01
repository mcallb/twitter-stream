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
        table = dynamodb.Table('distinct_follow_handle')
        table.put_item(
            Item={
                'handle': json.dumps(record['dynamodb']['Keys']['handle']['S']).strip('\"')
            }
        )

    return 'Successfully processed {} records.'.format(len(event['Records']))
