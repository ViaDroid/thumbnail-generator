import boto3
import os
import sys
import uuid
from urllib.parse import unquote_plus
from PIL import Image
import PIL.Image
import mimetypes

def resize_image(image_path, resized_path):
  with Image.open(image_path) as image:
      # tuple(x / 2 for x in image.size)
      size = 512, 512
      image.thumbnail(size)
      image.save(resized_path)

def resize_video(video_path, resized_path):
  type = mimetypes.MimeTypes().guess_type(video_path)
  #TODO

def lambda_handler(event, context):
  for record in event['Records']:
      print("event: ", event)
      bucket = record['s3']['bucket']['name']
      key = unquote_plus(record['s3']['object']['key'])
      handle_object(bucket, key)


def handle_object(bucket, key):
  session = boto3.Session()
  s3 = session.client('s3')
  # s3 = session.resource('s3')

  tmpkey = key.replace('/', '')
  download_path = '/tmp/{}{}'.format(uuid.uuid4(), tmpkey)
  upload_path = '/tmp/resized-{}'.format(tmpkey)
  s3.download_file(bucket, key, download_path)
  type = mimetypes.MimeTypes().guess_type(download_path)
  # print(type)

  try:
    if type is None or type[0] is None:
        upload_path = download_path
    elif type[0].startswith("image/"):
        resize_image(download_path, upload_path)
    elif type[0].startswith("video/"):
        resize_video(download_path, upload_path)
        upload_path = download_path
    else :
        upload_path = download_path
  except Exception as e:
    print("Exception: ", e, key)
    upload_path = download_path
  
  # upload
  s3.upload_file(upload_path, '{}-resized'.format(bucket), key)

  # clean tmp cache
  if download_path == upload_path :
    os.remove(download_path)
  else :
    os.remove(download_path)
    os.remove(upload_path)
