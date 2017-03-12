# twitter-stream
Monitors specific twitter handles for keywords and sends a message to sns.

# Build

docker build -t twitter-stream .

# Run 
sudo docker run -d \
-e "AWS_ACCESS_KEY_ID=<YOUR_KEY>" \
-e "AWS_SECRET_ACCESS_KEY=<YOUR_KEY>" \
-e "AWS_DEFAULT_REGION=us-east-1" \
--name twitter-stream twitter-stream:latest
