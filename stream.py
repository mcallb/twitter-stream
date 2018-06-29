import tweepy
import json
import boto3
import requests
import os
from urllib2 import Request, urlopen, URLError, HTTPError

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


def get_follow_filer():
    request = requests.get('https://dev.sudsfinder.com/filter/handle')
    handles = request.json()
    handles = map(str, handles['handle'])
    return handles


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

def is_running_in_aws(metadata='http://169.254.169.254/latest/meta-data/'):
    # from urllib2 import Request, urlopen, URLError, HTTPError
    req = Request(metadata)
    try:
        response = urlopen(req)
        return True
    except HTTPError as e:
        print 'Error code: ', e.code
        return False
    except URLError as e:
        print 'Reason: ', e.reason
        return False


# Override the StreamListener class
class MyStreamListener(tweepy.StreamListener):
    tweepy.debug(True)

    def on_status(self, status):
        if status.retweeted:
            return
        if status.lang != "en":
            return
        if status.text.startswith('RT'):
            return
        if status.in_reply_to_status_id is not None:
            return
        if status.in_reply_to_user_id is not None:
            return
        if status.in_reply_to_screen_name is not None:
            return
        # Save tweet from the search filter for debugging
        put_dynamodb(status)

        # If any of the words in search filter match we are interested in the tweet and it's send to the queue
        count = 0
        for word in SEARCH_FILTER:
            if word in status.text.lower():
                count += 1
                send_sqs(status, word)
            # Sends only the first occurance to sns
            if count == 1:
                send_sns(status.text)

    def on_error(self, status_code):
        print 'Exception...'
        print status_code
        if status_code == 420:
            print "Status code: %s" % status_code
            return True

    def on_timeout(self):
        print 'Timeout...'
        return True

    def on_exception(self, exception):
        print 'Exception...'
        print exception
        return True

if __name__ == '__main__':
    
    # If running on an ec2 instance get secrets from parameter store
    if is_running_in_aws():
        parameters = get_parameters_by_path('/sudsfinder')
        os.environ['CONSUMER_KEY']         = parameters['/sudsfinder/twitter-consumer-key']
        os.environ['CONSUMER_SECRET']      = parameters['/sudsfinder/twitter-consumer-secret']
        os.environ['ACCESS_TOKEN']         = parameters['/sudsfinder/twitter-access-token']
        os.environ['ACCESS_TOKEN_SECRET']  = parameters['/sudsfinder/twitter-access-token-secret']

    CONSUMER_KEY        = os.environ['CONSUMER_KEY']
    CONSUMER_SECRET     = os.environ['CONSUMER_SECRET']
    ACCESS_TOKEN        = os.environ['ACCESS_TOKEN']
    ACCESS_TOKEN_SECRET = os.environ['ACCESS_TOKEN_SECRET']
    
    SEARCH_FILTER = ['fort hill brewery','@FortHillBeer','@lamplighterbrew','@finbackbrewery','trilliumbrewing',
                     'trillium','maine beer company','maine beer co','foleybrothers','foley brothers','sazerac',
                     'sip of sunshine','lawsonsfinest','lawsons','rhinegeist','beer\'d']
    # FOLLOW_FILTER = get_follow_filer()
    # @RedstoneLiquors: 109292604
    # @rapidliquors: 198174347
    # @mcallb: 14584420
    FOLLOW_FILTER = ['109292604','198174347','14584420','2360048978']

    # Convert to lowercase for searching
    SEARCH_FILTER = map(lambda x: x.lower(), SEARCH_FILTER)

    print "Starting main..."
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    api = tweepy.API(
        auth,
        retry_count = 3,
        retry_delay = 5,
        retry_errors = set([401, 404, 500, 503]),
        wait_on_rate_limit = True,
        wait_on_rate_limit_notify = True
    )

    myStreamListener = MyStreamListener()
    myStream = tweepy.Stream(auth=api.auth, listener=myStreamListener)
    myStream.filter(follow=FOLLOW_FILTER, async=True)
    # myStream.filter(track="python", async=True)



