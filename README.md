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

## Licensing
------
ThumbnailGenerator is licensed under the [Apache License 2.0](https://github.com/ViaDroid/thumbnail-generator/blob/main/LICENSE).