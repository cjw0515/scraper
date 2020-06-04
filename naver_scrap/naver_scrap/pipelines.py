# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy import signals
import datetime
import logging
import boto3
from botocore.exceptions import ClientError
from scrapy.exporters import CsvItemExporter, JsonItemExporter
from scrapy.exceptions import DropItem
import gzip, shutil, io, os


def upload_file(a_key, s_key, file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3', aws_access_key_id=a_key, aws_secret_access_key=s_key)
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True


def mk_gz(file, gz_name):
    with open(file.name, 'rb') as f_in:
        with gzip.open(gz_name, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


class NaverScrapPipeline:
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            s3_access_key_id=crawler.settings.get('AWS_ACCESS_KEY_ID'),
            s3_access_key_secret=crawler.settings.get('AWS_SECRET_ACCESS_KEY'),
            prefix=crawler.settings.get('BUCKET_PREFIX'),
            bucket_name=crawler.settings.get('BUCKET_NAME')
        )

    def __init__(self, s3_access_key_id, s3_access_key_secret, prefix, bucket_name):
        self.s3_access_key_id = s3_access_key_id
        self.s3_access_key_secret = s3_access_key_secret
        self.prefix = prefix
        self.bucket_name = bucket_name
        self.total_cnt = 1
        self.del_line_num = 100

    # 스파이더가 오픈될때 호출됨
    def open_spider(self, spider):
        self.file = open('result.csv', 'wb')
        self.exporter = CsvItemExporter(self.file, encoding='utf-8')
        self.exporter.start_exporting()

    # 스파이더가 닫힐때 호출됨
    def close_spider(self, spider):
        self.exporter.finish_exporting()

    # 매 파이프라인 컴포넌트마다 호출됨.
    def process_item(self, item, spider):
        if self.total_cnt % self.del_line_num == 0:
            self.file.close()
            gz_name = '{0}.gz'.format(self.file.name)
            mk_gz(self.file, gz_name)

            dt = datetime.datetime.now()
            object_name = 'year={0}/month={1}/day={2}/'.format(dt.year, dt.strftime('%m'), dt.strftime('%d'))
            bucket_path = self.prefix + object_name + gz_name

            upload_file(
                self.s3_access_key_id,
                self.s3_access_key_secret,
                gz_name,
                self.bucket_name,
                bucket_path
            )

            self.file = open('result{0}.csv'.format(round(self.total_cnt / self.del_line_num)), 'wb')
            self.exporter = CsvItemExporter(self.file, encoding='utf-8')

        self.total_cnt += 1
        self.exporter.export_item(item)
        return item



