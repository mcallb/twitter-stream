import os
from twitter import MyStreamListener
from tweepy import API, OAuthHandler, Stream
from aws import send_sns, send_sqs
from process_tweet import get_store_filter

CONSUMER_KEY        = os.environ['CONSUMER_KEY']
CONSUMER_SECRET     = os.environ['CONSUMER_SECRET']
ACCESS_TOKEN        = os.environ['ACCESS_TOKEN']
ACCESS_TOKEN_SECRET = os.environ['ACCESS_TOKEN_SECRET']

def main():

    print("Starting main...")
    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    
    api = API(
        auth,
        retry_count = 3,
        retry_delay = 5,
        retry_errors = set([401, 404, 500, 503]),
        wait_on_rate_limit = True,
        wait_on_rate_limit_notify = True
    )

    listener = MyStreamListener()
    stream = Stream(auth=api.auth, listener=listener)
    store_filter = get_store_filter()
    stream.filter(follow=store_filter, is_async=True)

if __name__ == "__main__":
    main()
