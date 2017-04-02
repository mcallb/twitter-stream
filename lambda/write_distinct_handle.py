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

        tableKey = json.dumps(record['dynamodb']['Keys']['handle']['S']).strip('\"')
        print("This is talbeKey" + tableKey)

        # On insert add the item to the table
        if (record['eventName'] == "INSERT"):
            table.put_item(
                Item={
                    'handle': tableKey
                }
            )

        # On delete remove the item from the table
        elif (record['eventName'] == "REMOVE"):
            table.delete_item(
                Key={
                    'handle': tableKey
                }
            )

        else:
            print("Nothing to do. EventName = " + record['eventName'])

    return 'Successfully processed {} records.'.format(len(event['Records']))
