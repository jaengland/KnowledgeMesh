# KnowledgeMesh Local Container

## Purpose:
This container is designed to provide an environment with postgres, logstash, and elasticsearch.
Best practices were sometimes sacrificed for ease of use in a local environment.
<b>DO NOT DEPLOY THIS TO PRODUCTION</b>

## Use:
- `cd` to this directory
- `docker build -t multi-service-stack .`
- `docker run -p 5432:5432 -p 9200:9200 multi-service-stack`

## TODO:
- add authentication to elastic search
