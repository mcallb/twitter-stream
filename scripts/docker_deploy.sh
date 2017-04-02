#!/usr/bin/env bash

aws_access_key=`credstash get mcallb`

docker pull mcallb/twitter-stream:latest
docker stop twitter-stream
docker rm twitter-stream
docker rmi mcallb/twitter-stream:current
docker tag mcallb/twitter-stream:latest mcallb/twitter-stream:current
docker run -d \
    --restart always \
    --env "AWS_ACCESS_KEY_ID=AKIAJUZEOPB5NNQHJORA" \
    --env "AWS_SECRET_ACCESS_KEY=$aws_access_key" \
    --env "AWS_DEFAULT_REGION=us-east-1" \
    --name twitter-stream twitter-stream:latest