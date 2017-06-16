import tweepy
import json
import os
import boto3
from credstash import getSecret
import pymysql.cursors

# @RedstoneLiquors: 109292604
# @rapidliquors: 198174347
# @mcallb: 14584420

def get_filter(table_name):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)


def get_follow_filer():
    # Connect to the database
    # sudsfinder:PASSWORD@sudsfinder.c3hhbip7c3ty.us-east-1.rds.amazonaws.com:3306/sudsfinder
    connection = pymysql.connect(host='sudsfinder.c3hhbip7c3ty.us-east-1.rds.amazonaws.com',
                                 user='sudsfinder',
                                 password=getSecret('sudsfinder'),
                                 db='sudsfinder',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT `handle_user_id` FROM `handle`"
            cursor.execute(sql)
            result = cursor.fetchall()
            return result
    finally:
        connection.close()


def get_search_filter(table_name):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    response = table.scan()
    for x in response['Items']:
        print x

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

        # If any of the words in search filter match
        # we are interested in the tweet
        if any(x in status.text.lower() for x in SEARCH_FILTER):
            print "Filter triggered"
            session = boto3.Session()
            sns = session.client('sns')
            sns.publish(TopicArn='arn:aws:sns:us-east-1:354280536914:SendSms', Message="Sent via topic: %s" % status.text)


        # Add any tweets from the stream to a dynamodb table
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
        # print status.user.screen_name, status.id, status.created_at, status.source, status.text

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

    # handles = get_follow_filer()
    # FOLLOW_FILTER = []
    # for handle in handles:
    #     FOLLOW_FILTER.append(handle["handle_user_id"])

    CONSUMER_KEY = getSecret('twitter-consumer-key')
    CONSUMER_SECRET = getSecret('twitter-consumer-secret')
    ACCESS_TOKEN = getSecret('twitter-access-token')
    ACCESS_TOKEN_SECRET = getSecret('twitter-access-token-secret')

    # Use environment variables if they are defined or use default values instead.
    # The input parameter for filter is expecting a list but env vars are strings
    # so we need to convert them to a list using eval.

    FOLLOW_FILTER = ['109292604','198174347','14584420','2360048978']
    SEARCH_FILTER = ['fort hill brewery','@FortHillBeer','@lamplighterbrew','@finbackbrewery','trilliumbrewing',
                     'trillium','maine beer company','maine beer co','foleybrothers','foley brothers','sazerac',
                     'sip of sunshine','lawsonsfinest','lawsons','beer\'d', 'rhinegeist']

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
    #myStream.filter(track="python", async=True)
