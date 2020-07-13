# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html


import scrapy
from datetime import datetime
from scrapy.loader.processors import Join, MapCompose, TakeFirst

def date_format(value):
    """
    :param value: 날짜 string - 20180527121707 or 20191225 or 2019.05.
    :return: 2018-05-27
    """
    # replace(".", "-") + "01"
    return '{}-{}-{}'.format(value[:4], value[4:6], value[6:8])

def add_quote(value):
    """
    쌍따옴표 추가
    :param value: string
    :return: "{string}"
    """
    return '\"' + value + '\"' if value else ""

def get_fixeddate(value):
    return datetime.now().strftime("%Y-%m-%d %X")

class DaangnRnkKwd(scrapy.Item):
    rnk = scrapy.Field(output_processor=TakeFirst())
    kwd = scrapy.Field(
        input_processor=MapCompose(add_quote),
        output_processor=TakeFirst()
    )
    indecrease = scrapy.Field(output_processor=TakeFirst())
    fixeddate = scrapy.Field(
        input_processor=MapCompose(get_fixeddate),
        output_processor=TakeFirst()
    )
    type = scrapy.Field(output_processor=TakeFirst())

    pass

class DaangnPopItems(scrapy.Item):
    title = scrapy.Field(
        input_processor=MapCompose(add_quote),
        output_processor=TakeFirst()
    )
    cate = scrapy.Field(output_processor=TakeFirst())
    price = scrapy.Field(output_processor=TakeFirst())
    interest = scrapy.Field(output_processor=TakeFirst())
    chat = scrapy.Field(output_processor=TakeFirst())
    view = scrapy.Field(output_processor=TakeFirst())
    region1 = scrapy.Field(output_processor=TakeFirst())
    region2 = scrapy.Field(output_processor=TakeFirst())
    region3 = scrapy.Field(output_processor=TakeFirst())
    fixeddate = scrapy.Field(
        input_processor=MapCompose(get_fixeddate),
        output_processor=TakeFirst()
    )
    type = scrapy.Field(output_processor=TakeFirst())

    pass
