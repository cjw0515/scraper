import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from ec2_metadata import ec2_metadata

instance_id_map = {
    'i-092bd6ef6bbd11da9': 'bot1',
    'i-07574e96d20a9bf53': 'bot2',
    'i-01a075a7a41086a94': 'bot3',
    'i-0260f944a2702f555': 'bot4',
    'i-094612ed9001326db': 'bot5',
}

try:
    INSTANCE_ID = instance_id_map[ec2_metadata.instance_id]
except Exception as e:
    INSTANCE_ID = 'local-pc'

BOT_NAME = INSTANCE_ID

AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']

BUCKET_NAME = 'bi-temp'
BUCKET_PREFIX = 'datalake/crawling/'

if os.environ['ENV'] == 'dev':
    FILE_REMOVE = False
    LOG_LEVEL = 'INFO'
else:
    FILE_REMOVE = True
    LOG_LEVEL = 'ERROR'