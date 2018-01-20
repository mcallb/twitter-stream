import tweepy
import json
import boto3
import requests
import os

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
    session = boto3.Session()
    sns = session.client('sns')
    sns.publish(TopicArn='arn:aws:sns:us-east-1:121050202290:SendSns', Message="Sent via topic: %s" % message)


def put_dynamodb(status):
    dynamodb = boto3.resource('dynamodb')
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
        for word in SEARCH_FILTER:
            if word in status.text.lower():
                send_sqs(status, word)
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
    CONSUMER_KEY        = os.environ['CONSUMER_KEY']
    CONSUMER_SECRET     = os.environ['CONSUMER_SECRET']
    ACCESS_TOKEN        = os.environ['ACCESS_TOKEN']
    ACCESS_TOKEN_SECRET = os.environ['ACCESS_TOKEN_SECRET']
    
    SEARCH_FILTER = ['fort hill brewery','@FortHillBeer','@lamplighterbrew','@finbackbrewery','trilliumbrewing',
                     'trillium','maine beer company','maine beer co','foleybrothers','foley brothers','sazerac',
                     'sip of sunshine','lawsonsfinest','lawsons','rhinegeist','beer\'d']
    FOLLOW_FILTER = get_follow_filer()
    # @RedstoneLiquors: 109292604
    # @rapidliquors: 198174347
    # @mcallb: 14584420
    # FOLLOW_FILTER = ['109292604','198174347','14584420','2360048978']

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



