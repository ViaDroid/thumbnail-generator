import boto3
import queue
import threading
import json
import argparse
import time
import os

default_region = 'us-west-2'
default_function = 'thumbnail-generator'
bucket_dev = 'com.landingintl.assets-dev-us-west-2'
bucket_qa = 'com.landingintl.assets-qa-us-west-2'
bucket_prod = 'com.landingintl.assets-us-west-2'

bucket_map = {
    'dev':bucket_dev,
    'qa':bucket_qa,
    'prod':bucket_prod,
}


parser = argparse.ArgumentParser()
parser.add_argument('--version', '-v', action='version',
                    version='%(prog)s version : v 0.01', help='show the version')
group = parser.add_mutually_exclusive_group()
group.add_argument("--env", '-e', default='dev', help='environment [dev|qa|prod] for s3 bucket')
group.add_argument("--bucket", '-b', help='aws s3 bucket name')

parser.add_argument("--region", '-r', default=default_region, help='aws region')
parser.add_argument("--function", '-f', default=default_function, help='aws lambda function name')
parser.add_argument("--thread-num", '-t', default=10, type=int, help='concurrency thread num, default 10')
parser.add_argument("--file-type", '-ft', help='file format type')
# parser.add_argument("--statistics", '-s', help='Statistics by format')

args = parser.parse_args()
region = args.region
env = args.env
bucket = args.bucket
function = args.function
thread_num = args.thread_num
file_type = args.file_type

s3_client = boto3.client('s3')
lambda_client = boto3.client('lambda', region)

semaphore = threading.Semaphore(value=0)

statistics_map = {}

payload_template = {
    "Records": [
        {
            "eventVersion": "2.0",
            "eventSource": "aws:s3",
            "awsRegion": "us-east-1",
            "eventTime": "1970-01-01T00:00:00.000Z",
            "eventName": "ObjectCreated:Put",
            "userIdentity": {
                "principalId": "EXAMPLE"
            },
            "requestParameters": {
                "sourceIPAddress": "127.0.0.1"
            },
            "responseElements": {
                "x-amz-request-id": "EXAMPLE123456789",
                "x-amz-id-2": "EXAMPLE123/5678abcdefghijklambdaisawesome/mnopqrstuvwxyzABCDEFGH"
            },
            "s3": {
                "s3SchemaVersion": "1.0",
                "configurationId": "testConfigRule",
                "bucket": {
                    "name": "com.landingintl.assets-dev-us-west-2",
                    "ownerIdentity": {
                        "principalId": "EXAMPLE"
                    },
                    "arn": "arn:aws:s3:::com.landingintl.assets-dev-us-west-2"
                },
                "object": {
                    "key": "_YKfIjqkRJG8voRLFun2Gw/0046b7b84032dedd0c5bb9e2e8085e5c.jpeg",
                    "size": 1024,
                    "eTag": "64635c1230cd7b9fa27becfa5bcd9831",
                    "sequencer": "0A1B2C3D4E5F678901"
                }
            }
        }
    ]
}


def loop_bucket(bucket):
    # Create a reusable Paginator
    paginator = s3_client.get_paginator('list_objects')

    # Create a PageIterator from the Paginator
    page_iterator = paginator.paginate(Bucket=bucket)

    q = queue.Queue()
    for page in page_iterator:
        # print(page['Contents'])
        for obj in page['Contents']:
            key = obj['Key']
            size = obj['Size']

            suffix = os.path.splitext(key)[-1][1:]
            if suffix not in statistics_map:
                statistics_map[suffix] = [1, size]
            else:
                v = statistics_map[suffix]
                v[0] += 1
                v[1] += size
                statistics_map[suffix] = v
            
            if file_type is not None:
                if key.endswith(file_type):
                    q.put([size, key])
            else:
                q.put([size, key])
    
    return q

def start(q):
    threads = []
    for i in range(thread_num):
        t = threading.Thread(target=worker, args=(q,))
        threads.append(t)

    for i in range(thread_num):
        threads[i].start()

    for i in range(thread_num):
        threads[i].join()


def worker(q):
    while True:
        if q.empty():
            return
        else:
            semaphore.release()
            t = q.get()
            print("count:", semaphore._value, t[1])

            payload_template['Records'][0]['s3']['object']['size'] = t[0]
            payload_template['Records'][0]['s3']['object']['key'] = t[1]
            send_event(payload_template)

            if semaphore._value % 100 == 0:
                print("progress count: ", semaphore._value)


def send_event(payload):
    r = lambda_client.invoke(FunctionName=function,
                         InvocationType='Event',
                         Payload=json.dumps(payload))
    print(r)


def print_statistics():
    count = size = 0
    for k, v in statistics_map.items():
        count += v[0]
        size += v[1]
        print('{}\t\t{}\t{:.2f} Mb'.format(k, v[0], v[1]/1000/1000))
    
    print('\nTotal:\t\t{}\t{:.2f} Mb'.format(count, size/1000/1000))


if __name__ == '__main__':
    start_time = time.time()

    if bucket is None :
        bucket = bucket_map[env]

    print(region, bucket, function, thread_num)

    # session = boto3.Session(aws_access_key_id='<your_access_key_id>',
    #               aws_secret_access_key='<your_secret_access_key>')
    

    # print(payload_template)
    payload_template['Records'][0]['awsRegion'] = region
    payload_template['Records'][0]['s3']['bucket']['name'] = bucket
    payload_template['Records'][0]['s3']['bucket']['arn'] = 'arn:aws:s3:::{}'.format(bucket)

    q = loop_bucket(bucket)
    # print("Count: ", q.qsize())
    print_statistics()

    start(q)

    # send_event(payload_template)

    print("Duration time:", time.time() - start_time)
    
