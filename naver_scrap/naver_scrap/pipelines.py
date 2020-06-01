# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy import signals
from scrapy.exporters import CsvItemExporter, JsonItemExporter
from scrapy.exceptions import DropItem
import gzip, shutil, io


class NaverScrapPipeline:
    # def __init__(self):
    #     self.file = open('result.json', 'wb')
    #     self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
    #     self.exporter.start_exporting()

    # 스파이더가 오픈될때 호출됨
    def open_spider(self, spider):
        # self.file = open('result.json', 'wb')
        # self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        # self.exporter.start_exporting()
        self.file = open('result.csv', 'wb')
        self.exporter = CsvItemExporter(self.file)
        self.exporter.start_exporting()

    # 스파이더가 닫힐때 호출됨
    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()
        with open('result.csv', 'rb') as f_in:
            with gzip.open('test.gz', 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

    # 매 파이프라인 컴포넌트마다 호출됨.
    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item
