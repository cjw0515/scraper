# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import sys

sys.path.append("C:/anaconda3/envs/scraper-10x10/Lib/site-packages")

from scrapy import signals
from scrapy.utils.project import get_project_settings
from utils.job_executer import exec_next_job

import datetime
import logging
import boto3
from botocore.exceptions import ClientError
from scrapy.exporters import CsvItemExporter, JsonItemExporter
from scrapy.exceptions import DropItem
import gzip, shutil, io, os
import re


dir = os.path.join(get_project_settings().get('PROJECT_ROOT_PATH'), r"drivers/chromedriver")

FILE_EXSENSION = '.csv'
CSV_HEAD = False
ISUPLOAD = True

def file_chk(origin_path, file_exs):
    p = re.compile(r"(.+)\(([1-9])\)(.+)?")
    m = p.match(origin_path)

    if os.path.isfile(origin_path):
        if m is not None:
            idx = int(m.group(2))
            idx += 1
            changed_path = re.sub(p, r'\1({})\3'.format(idx), origin_path)
            return file_chk(changed_path, file_exs)
        else:
            changed_path = origin_path[:origin_path.find(file_exs)] + '(2)' + origin_path[origin_path.find(file_exs):]
            return file_chk(changed_path, file_exs)
    else:
        return origin_path

def s3_upload_file(a_key, s_key, file_name, file_path, bucket, object_path=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_path: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # Upload the file
    s3_client = boto3.client('s3', aws_access_key_id=a_key, aws_secret_access_key=s_key)
    obj_full_path = object_path + file_name
    try:
        res = s3_client.head_object(Bucket=bucket, Key=obj_full_path)
    except ClientError as e:
        # 파일 존재하지 않을 때
        if e.response['Error']['Code'] == '404':
            try:
                s3_client.upload_file(file_path, bucket, obj_full_path)
            except ClientError as e:
                logging.error(e)
                return False
            return True
    else:
        # 파일 존재할 시 파일 명 수정해서 다시 콜
        p = re.compile(r"(.+)\(([1-9])\)(.+)?")
        m = p.match(file_name)
        if m is not None:
            idx = int(m.group(2))
            idx += 1
            changed_path = re.sub(p, r'\1({})\3'.format(idx), file_name)
            return s3_upload_file(a_key, s_key, changed_path, file_path, bucket, object_path=object_path)
        else:
            changed_path = file_name[:file_name.find(".csv")] + '(2)' + file_name[file_name.find(".csv"):]
            return s3_upload_file(a_key, s_key, changed_path, file_path, bucket, object_path=object_path)



def mk_gz(file, gz_name):
    with open(file.name, 'rb') as f_in:
        with gzip.open(gz_name, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


class NaverScrapPipeline:
    @classmethod
    def from_crawler(cls, crawler):
        crawl_op_stat = {
            # best
            'crawl_item': crawler.settings.get('CRAWL_ITEM') or None,
            'crawl_keyword': crawler.settings.get('CRAWL_KEYWORD') or None,
            'crawl_brand': crawler.settings.get('CRAWL_BRAND') or None,
            # trend
            'crawl_trend': True,
            # category
            'crawl_category': True,
        }
        chain = crawler.spider.use_crawl_chain or 1
        return cls(
            s3_access_key_id=crawler.settings.get('AWS_ACCESS_KEY_ID'),
            s3_access_key_secret=crawler.settings.get('AWS_SECRET_ACCESS_KEY'),
            bucket_path_prefix=crawler.settings.get('BUCKET_PREFIX'),
            bucket_name=crawler.settings.get('BUCKET_NAME'),
            instance_id=crawler.settings.get('INSTANCE_ID'),
            file_remove=crawler.settings.get('FILE_REMOVE'),
            crawl_op_stat=crawl_op_stat,
            chain=chain
        )

    def __init__(self, s3_access_key_id, s3_access_key_secret, bucket_path_prefix,
                 bucket_name, instance_id, file_remove, crawl_op_stat, chain):
        self.s3_access_key_id = s3_access_key_id
        self.s3_access_key_secret = s3_access_key_secret
        self.bucket_path_prefix = bucket_path_prefix
        self.bucket_name = bucket_name
        self.instance_id = instance_id
        self.file_remove = file_remove
        self.chain = chain
        # 베스트 아이템
        self.item_conf = {
            'total_line': 1,
            'del_line_num': 3000,
            'file': None,
            'file_name': 'best_item-{0}.csv'.format(instance_id),
            'exporter': None,
            'fields_to_export': ['brand', 'cate_id', 'cate_name', 'depth', 'female_rate', 'image_url', 'item_nm',
                                 'item_url', 'manufacturer', 'min_price', 'nv_mid', 'prefer_age1', 'prefer_age2',
                                 'rate', 'reg_date', 'review_cnt', 'rnk', 'seller_cnt', 'single_mall_nm',
                                 'storefarm_num', 'top_store_num', 'type', 'wish_cnt'],
            'is_upload': ISUPLOAD,
            'op_stat': crawl_op_stat['crawl_item'],
            's3_group': 'nvshop_best_item'
        }
        # 베스트 키워드
        self.kwd_conf = {
            'total_line': 1,
            'del_line_num': 3000,
            'file': None,
            'file_name': 'best_kwd-{0}.csv'.format(instance_id),
            'exporter': None,
            'fields_to_export': ['cate_id', 'fixeddate', 'gb', 'keyword', 'period', 'rnk', 'trend', 'type'],
            'is_upload': ISUPLOAD,
            'op_stat': crawl_op_stat['crawl_keyword'],
            's3_group': 'nvshop_best_keyword'
        }
        # 베스트 브랜드
        self.brd_conf = {
            'total_line': 1,
            'del_line_num': 3000,
            'file': None,
            'file_name': 'best_brd-{0}.csv'.format(instance_id),
            'exporter': None,
            'fields_to_export': ['cate_id', 'fixeddate', 'gb', 'keyword', 'period', 'rnk', 'trend', 'type'],
            'is_upload': ISUPLOAD,
            'op_stat': crawl_op_stat['crawl_brand'],
            's3_group': 'nvshop_best_brand'
        }
        # 트렌드 키워드
        self.trend_kwd_conf = {
            'total_line': 1,
            'del_line_num': 3000,
            'file': None,
            'file_name': 'trend_kwd-{0}.csv'.format(instance_id),
            'exporter': None,
            'fields_to_export': ['keyword', 'period', 'type', 'value'],
            'is_upload': ISUPLOAD,
            'op_stat': crawl_op_stat['crawl_trend'],
            's3_group': 'dlabtrend'
        }
        # 카테고리 아이템
        self.category_item_conf = {
            'total_line': 1,
            'del_line_num': 6000,
            'file': None,
            'file_name': 'category_item-{0}.csv'.format(instance_id),
            'exporter': None,
            'fields_to_export': ['cate_id', 'fixeddate', 'image_url', 'item_nm', 'item_url', 'max_price', 'min_price',
                                 'nv_mid', 'rate', 'reg_date', 'review_cnt', 'rnk', 'seller_cnt', 'single_mall_nm',
                                 'type', 'wish_cnt'],
            'is_upload': ISUPLOAD,
            'op_stat': crawl_op_stat['crawl_category'],
            's3_group': 'nvshop_category_item'
        }
        # 크롤링 묶음
        self.data_conf_cont = {
            'naver_best_category': [self.item_conf, self.kwd_conf, self.brd_conf],
            'naver_datalab_trend': [self.trend_kwd_conf],
            'naver_category': [self.category_item_conf],
        }

    # 스파이더가 오픈될때 호출됨
    def open_spider(self, spider):
        for conf in self.data_conf_cont[spider.name]:
            if conf['op_stat']:
                file_name = file_chk('1_' + conf['file_name'], FILE_EXSENSION)
                conf['file'] = open(file_name, 'wb')
                conf['exporter'] = CsvItemExporter(conf['file'],
                                                   encoding='utf-8',
                                                   include_headers_line=CSV_HEAD)
                conf['exporter'].fields_to_export = conf['fields_to_export']
                conf['exporter'].start_exporting()

    # 스파이더가 닫힐때 호출됨
    def close_spider(self, spider):
        for conf in self.data_conf_cont[spider.name]:
            if conf['op_stat']:
                self.close_exporter(conf['file'], s3_group=conf['s3_group'], is_upload=conf['is_upload'])
                conf['exporter'].finish_exporting()
        # 다음 job 실행
        if self.chain == 1: exec_next_job(spider.name)

    # 매 파이프라인 컴포넌트마다 호출됨.
    def process_item(self, item, spider):
        # 빈값 채우기
        for field in item.fields:
            item.setdefault(field, '')
        try:
            if self.item_conf['op_stat'] and item['type'] == 'nvshop_best_item':
                self.data_save(item, self.item_conf)
            if self.kwd_conf['op_stat'] and item['type'] == 'nvshop_best_keyword':
                self.data_save(item, self.kwd_conf)
            if self.brd_conf['op_stat'] and item['type'] == 'nvshop_best_brand':
                self.data_save(item, self.brd_conf)
            if self.trend_kwd_conf['op_stat'] and item['type'] == 'dlabtrend':
                self.data_save(item, self.trend_kwd_conf)
            if self.category_item_conf['op_stat'] and item['type'] == 'nvshop_category_item':
                self.data_save(item, self.category_item_conf)
        except Exception as e:
            print('pipeline error: ', e)
            pass

        return item

    def data_save(self, item, conf):
        if conf['total_line'] % conf['del_line_num'] == 0:
            # 스트림 닫고 업로드
            self.close_exporter(conf['file'], s3_group=conf['s3_group'], is_upload=conf['is_upload'])
            file_name = file_chk('{0}_{1}'.format(round(conf['total_line'] / conf['del_line_num'] + 1), conf['file_name'])
                                 , FILE_EXSENSION)
            conf['file'] = open(file_name, 'wb')
            conf['exporter'] = CsvItemExporter(conf['file'], encoding='utf-8', include_headers_line=CSV_HEAD)
            conf['exporter'].fields_to_export = conf['fields_to_export']

        conf['total_line'] += 1
        conf['exporter'].export_item(item)

    # 파일 스트림 닫기 / 업로드
    def close_exporter(self, file_stream, s3_group, is_upload):
        file_stream.close()
        gz_name = '{0}.gz'.format(file_stream.name)
        mk_gz(file_stream, gz_name)

        dt = datetime.datetime.now()
        object_name = '{0}/year={1}/month={2}/day={3}/'.format(s3_group, dt.year, dt.strftime('%m'),
                                                               dt.strftime('%d'))
        bucket_path = self.bucket_path_prefix + object_name

        if is_upload:
            s3_upload_file(
                self.s3_access_key_id,
                self.s3_access_key_secret,
                gz_name,
                gz_name,
                self.bucket_name,
                bucket_path
            )
        if self.file_remove:
            os.remove(file_stream.name)
            os.remove(gz_name)
