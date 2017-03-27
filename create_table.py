from __future__ import print_function # Python 2/3 compatibility
import boto3

def stream_table(resource):
    table = resource.create_table(
        TableName='stream',
        KeySchema=[
            {
                'AttributeName': 'screen_name',
                'KeyType': 'HASH'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'screen_name',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        }
    )
    print("Table status:", table.table_status)

def follow_handle(resource):
    table = resource.create_table(
        TableName='follow_handle',
        KeySchema=[
            {
                'AttributeName': 'handle',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'user_name',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'user_name',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'handle',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        }
    )
    print("Table status:", table.table_status)

def follow_search(resource):
    table = resource.create_table(
        TableName='follow_search',
        KeySchema=[
            {
                'AttributeName': 'search',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'user_name',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'user_name',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'search',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 1,
            'WriteCapacityUnits': 1
        }
    )
    print("Table status:", table.table_status)


def delete_table(resource, name):
    table = resource.Table(name)
    table.delete()
    print("Table status:", table.table_status)

if __name__ == '__main__':
    resource = boto3.resource('dynamodb', region_name='us-east-1')
    stream_table(resource)
    #follow_handle(resource)
    #follow_search(resource)
    #delete_table(resource, 'follow-stream')
