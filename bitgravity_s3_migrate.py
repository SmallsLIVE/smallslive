import hashlib
import os
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import pycurl

BITGRAVITY_SECRET = os.environ['BITGRAVITY_SECRET']
BITGRAVITY_CDN_URL = os.environ['BITGRAVITY_CDN_URL']
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']

conn = S3Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
bucket = conn.get_bucket('smallsliveaudio')

with open('ids.txt', 'r') as f:
    for event_id in f.readlines():
        event_id = event_id.strip()
        for slot in range(1, 7):  # possible slots <event_id>-[1-6].mp3
            filename = "{}-{}.mp3".format(event_id, slot)
            m = hashlib.md5()
            m.update(BITGRAVITY_SECRET + '/smallslive/secure/' + filename + "?e=0")
            hash = m.hexdigest()
            fp = open('temp.mp3', 'wb')
            curl = pycurl.Curl()
            url = "{}/secure/{}?e=0&h={}".format(BITGRAVITY_CDN_URL, filename, hash)
            curl.setopt(pycurl.URL, url)
            curl.setopt(pycurl.FOLLOWLOCATION, 1)
            curl.setopt(pycurl.WRITEDATA, fp)
            curl.perform()
            if curl.getinfo(pycurl.HTTP_CODE) == 200:
                print "{} found on bitgravity".format(filename)
                k = Key(bucket)
                k.key = filename
                k.set_contents_from_filename('temp.mp3')
                print "{} uploaded to S3".format(filename)
            else:
                print "{} NOT found".format(filename)
            os.remove('temp.mp3')