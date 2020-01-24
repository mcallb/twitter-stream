import boto3 
import json
import requests


def is_running_in_aws(metadata='http://169.254.169.254/latest/meta-data/'):
    # from urllib2 import Request, urlopen, URLError, HTTPError
    try:
        req = requests.get(metadata, timeout=2)
        return True
    except HTTPError as e:
        #print 'Error code: ', e.code
        return False
    except ConnectTimeout as e:
        #print 'Reason: ', e.code
        return False


def role_arn_to_session(**args):
    """
    Usage :
        session = role_arn_to_session(
            RoleArn='arn:aws:iam::012345678901:role/example-role',
            RoleSessionName='ExampleSessionName')
        client = session.client('sqs')
    """
    client = boto3.client('sts')
    response = client.assume_role(**args)
    return boto3.Session(
        aws_access_key_id=response['Credentials']['AccessKeyId'],
        aws_secret_access_key=response['Credentials']['SecretAccessKey'],
        aws_session_token=response['Credentials']['SessionToken'])


def send_sns(message):
    session = boto3.Session(region_name='us-east-1')
    sns = session.client('sns')
    sns.publish(TopicArn='arn:aws:sns:us-east-1:121050202290:SendSns', Message="Sent via topic: %s" % message)


def put_dynamodb(status):
    dynamodb = boto3.resource('dynamodb', region_name = 'us-east-1')
    table = dynamodb.Table('stream')
    table.put_item(
        Item={
            'screen_name': status.user.screen_name,
            'id': status.id,
            'created_at': str(status.created_at),
            'source': status.source,
            'text': status.text,
            'json': json.dumps(status._json),
            'user_id': status.user.id
        }
    )


def send_sqs(status, filter_word):
    session = boto3.Session(region_name='us-east-1')
    sqs = session.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName='twitter_message')
    message = {
        'screen_name': status.user.screen_name,
        'created_at': str(status.created_at),
        'text': status.text,
        'user_id': status.user.id,
        'filter_word': filter_word
    }
    response = queue.send_message(MessageBody=json.dumps(message))
    return response.get('MessageId')


def role_arn_to_session(**args):
    """
    Usage :
        session = role_arn_to_session(
            RoleArn='arn:aws:iam::012345678901:role/example-role',
            RoleSessionName='ExampleSessionName')
        client = session.client('sqs')
    """
    client = boto3.client('sts')
    response = client.assume_role(**args)
    return boto3.Session(
        aws_access_key_id=response['Credentials']['AccessKeyId'],
        aws_secret_access_key=response['Credentials']['SecretAccessKey'],
        aws_session_token=response['Credentials']['SessionToken'])


def get_parameters_by_path(path):
    """
    This function reads a secure parameter from AWS' SSM service.
    The request must be passed a valid parameter name, as well as 
    temporary credentials which can be used to access the parameter.
    The parameter's value is returned.
    """
    # Create the SSM Client
    session = role_arn_to_session(RoleArn='arn:aws:iam::354280536914:role/ssm_get_parameters',RoleSessionName='mcallb')
    ssm = session.client('ssm', region_name='us-east-1')

    # Get the requested parameter
    parameters = ssm.get_parameters_by_path(
        Path=path,
        WithDecryption=True,
        Recursive=True
    )
    
    # Store the credentials in a variable
    credentials = {}
    
    for param in parameters['Parameters']:
        credentials[param['Name']] = param['Value']
    
    return credentials