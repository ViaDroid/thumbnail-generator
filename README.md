# ThumbnailGenerator

This project contains source code and supporting files for a serverless application that you can deploy with the SAM CLI. It includes the following files and folders.

- src - Code for the application's Lambda function.
- events - Invocation events that you can use to invoke the function.
- template.yaml - A template that defines the application's AWS resources.


Build and Deploy:

## Build:
------
    ./deploy.sh --action build --zip-file function.zip

## Deploy & Update:
-------
    Create Function:
        ./deploy.sh --action create --zip-file function.zip

    Update Function Code:
        ./deploy.sh --action update --zip-file function.zip


## Test:
------
    aws --region=us-west-2 lambda invoke \
        --function-name thumbnail-generator \
        --invocation-type Event \
        --payload file://events/s3-image-put-test-dev.json outputfile.txt

## Generate thumbnail for exists objects
---
```shell
Usage:
    python3 thumbnail-generator/src/thumbnail_event_sender.py -h

    usage: thumbnail_event_sender.py [-h] [--version] [--bucket BUCKET] [--region REGION] [--function FUNCTION]

    options:
    -h, --help            show this help message and exit
    --version, -v         show the version
    --env ENV, -e ENV     environment [dev|qa|prod] for s3 bucket
    --bucket BUCKET, -b BUCKET
                            aws s3 bucket name
    --region REGION, -r REGION
                            aws region
    --function FUNCTION, -f FUNCTION
                            aws lambda function name
    --thread-num THREAD_NUM, -t THREAD_NUM
                            concurrency thread num, default 10
    --file-type FILE_TYPE, -ft FILE_TYPE
                            file format type

Dev:
    python3 src/thumbnail_event_sender.py -e=dev -f=thumbnail-generator -r=us-west-2

QA:
    python3 src/thumbnail_event_sender.py -e=qa -f=thumbnail-generator -r=us-west-2

Prod:
    python3 src/thumbnail_event_sender.py -e=prod -f=thumbnail-generator -r=us-west-2

Custom Bucket & Function:
    python3 src/thumbnail_event_sender.py -b=[bucket-name] -f=[function-name] -r=us-west-2
```

## Licensing
------
ThumbnailGenerator is licensed under the [Apache License 2.0](https://github.com/ViaDroid/thumbnail-generator/blob/main/LICENSE).