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

def extrace_int(val):
    return int(''.join(i for i in val if i.isdigit()) or 0)

class NaverCategoryItem(scrapy.Item):
    # define the fields for your item here like:
    cate_id = scrapy.Field(output_processor=TakeFirst())
    rnk = scrapy.Field(output_processor=TakeFirst())
    nv_mid = scrapy.Field(output_processor=TakeFirst())
    single_mall_nm = scrapy.Field(
        input_processor=MapCompose(add_quote),
        output_processor=TakeFirst()
    )
    item_url = scrapy.Field(output_processor=TakeFirst())
    rate = scrapy.Field(output_processor=TakeFirst())
    item_nm = scrapy.Field(
        input_processor=MapCompose(add_quote),
        output_processor=TakeFirst()
    )
    min_price = scrapy.Field(output_processor=TakeFirst())
    max_price = scrapy.Field(output_processor=TakeFirst())
    reg_date = scrapy.Field(
        input_processor=MapCompose(date_format),
        output_processor=TakeFirst()
    )
    wish_cnt = scrapy.Field(output_processor=TakeFirst())
    seller_cnt = scrapy.Field(output_processor=TakeFirst())
    review_cnt = scrapy.Field(output_processor=TakeFirst())
    image_url = scrapy.Field(output_processor=TakeFirst())
    fixeddate = scrapy.Field(
        input_processor=MapCompose(get_fixeddate),
        output_processor=TakeFirst()
    )
    type = scrapy.Field(output_processor=TakeFirst())

    pass


class NaverBestItem(scrapy.Item):
    # define the fields for your item here like:
    seller_cnt = scrapy.Field(output_processor=TakeFirst())
    single_mall_nm = scrapy.Field(
        input_processor=MapCompose(add_quote),
        output_processor=TakeFirst()
    )
    rate = scrapy.Field(output_processor=TakeFirst())
    prefer_age1 = scrapy.Field(output_processor=TakeFirst())
    prefer_age2 = scrapy.Field(output_processor=TakeFirst())
    female_rate = scrapy.Field(output_processor=TakeFirst())
    min_price = scrapy.Field(input_processor=MapCompose(extrace_int), output_processor=TakeFirst())
    manufacturer = scrapy.Field(output_processor=TakeFirst())
    brand = scrapy.Field(output_processor=TakeFirst())
    reg_date = scrapy.Field(output_processor=TakeFirst())
    wish_cnt = scrapy.Field(output_processor=TakeFirst())
    review_cnt = scrapy.Field(output_processor=TakeFirst())
    storefarm_num = scrapy.Field(output_processor=TakeFirst())
    top_store_num = scrapy.Field(output_processor=TakeFirst())
    image_url = scrapy.Field(output_processor=TakeFirst())
    cate_id = scrapy.Field(output_processor=TakeFirst())
    rnk = scrapy.Field(output_processor=TakeFirst())
    nv_mid = scrapy.Field(output_processor=TakeFirst())
    item_url = scrapy.Field(output_processor=TakeFirst())
    item_nm = scrapy.Field(
        input_processor=MapCompose(add_quote),
        output_processor=TakeFirst()
    )
    cate_name = scrapy.Field(output_processor=TakeFirst())
    depth = scrapy.Field(output_processor=TakeFirst())
    type = scrapy.Field(output_processor=TakeFirst())

    pass


class NaverBestKeyword(scrapy.Item):
    rnk = scrapy.Field(output_processor=TakeFirst())
    keyword = scrapy.Field(output_processor=TakeFirst())
    trend = scrapy.Field(output_processor=TakeFirst())
    fixeddate = scrapy.Field(
        input_processor=MapCompose(get_fixeddate),
        output_processor=TakeFirst()
    )
    cate_id = scrapy.Field(output_processor=TakeFirst())
    period = scrapy.Field(output_processor=TakeFirst())
    gb = scrapy.Field(output_processor=TakeFirst())
    type = scrapy.Field(output_processor=TakeFirst())

    pass


class NaverBestBrand(scrapy.Item):
    rnk = scrapy.Field(output_processor=TakeFirst())
    keyword = scrapy.Field(output_processor=TakeFirst())
    trend = scrapy.Field(output_processor=TakeFirst())
    fixeddate = scrapy.Field(
        input_processor=MapCompose(get_fixeddate),
        output_processor=TakeFirst()
    )
    cate_id = scrapy.Field(output_processor=TakeFirst())
    period = scrapy.Field(output_processor=TakeFirst())
    gb = scrapy.Field(output_processor=TakeFirst())
    type = scrapy.Field(output_processor=TakeFirst())

    pass


class NaverDataLabTrend(scrapy.Item):
    keyword = scrapy.Field(output_processor=TakeFirst())
    period = scrapy.Field(output_processor=TakeFirst())
    value = scrapy.Field(output_processor=TakeFirst())
    type = scrapy.Field(output_processor=TakeFirst())