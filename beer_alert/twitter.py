import tweepy
from aws import put_dynamodb
from process_tweet import process_tweet

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
        # Do something with the tweet
        process_tweet(status)

    def on_error(self, status_code):
        print('Exception...')
        print(status_code)
        if status_code == 420:
            print("Status code: %s" % status_code)
            return True

    def on_timeout(self):
        print('Timeout...')
        return True

    def on_exception(self, exception):
        print('Exception...')
        print(exception)
        return True
        