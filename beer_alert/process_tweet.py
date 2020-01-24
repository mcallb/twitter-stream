import yaml
from aws import send_sns, send_sqs


def process_tweet(status):
    # interested in the tweet and it's send to the queue
    # If any of the words in search filter match we are 
    count = 0
    for word in _get_beer_filter():
        if word in status.text.lower():
            count += 1
            send_sqs(status, word)
            # Sends only the first occurrance to sns
            if count == 1:
                send_sns(status.text)


def get_store_filter():
    
    return _get_filter_key('stores')


def _get_beer_filter():
    beer_filter = _get_filter_key('beers')
    
    return [x.lower() for x in beer_filter]

def _get_filter_key(key_name):
    with open("./data.yaml", 'r') as stream:
        contents = yaml.safe_load(stream)
    
    return contents[key_name]

    


