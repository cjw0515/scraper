# -*- coding: utf-8 -*-
import sys, os

sys.path.append("C:/anaconda3/envs/scraper-10x10/Lib/site-packages")
import scrapy
from scrapy.loader import ItemLoader
from ..items import NaverCategoryItem
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from fake_useragent import UserAgent
from urllib.parse import urlparse, parse_qs, parse_qsl, urlencode, urlunparse, urlsplit
import logging
from datetime import datetime
import requests

import re
import json

ua = UserAgent()
ZZIM_API_URL = "https://search.shopping.naver.com/product-zzim/products"
NUM_OF_ITEMS_PER_CATE = 90

def qs_replace(org_url, key_to_change, val_to_change):
    parts = urlparse(org_url)
    qs = dict(parse_qsl(parts.query))
    qs[key_to_change] = val_to_change
    parts = parts._replace(query=urlencode(qs))
    new_url = urlunparse(parts)

    return new_url

class NaverCategorySpider(scrapy.Spider):
    name = 'naver_category'
    custom_settings = {
        # 'AUTOTHROTTLE_ENABLED': True,
        # 'AUTOTHROTTLE_START_DELAY': 5,
        # 'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
        # 'DOWNLOAD_DELAY': 0.5,
        'ITEM_PIPELINES': {
            'naver_scrap.pipelines.NaverScrapPipeline': 300,
        },
        # 'SPIDER_MIDDLEWARES': {
        #     'naver_scrap.middlewares.NaverScrapSpiderMiddleware': 543,
        # },
        # 'DOWNLOADER_MIDDLEWARES': {
        #     'naver_scrap.middlewares.NaverScrapDownloaderMiddleware': 543,
        #     'naver_scrap.middlewares.SleepRetryMiddleware': 100,
        # }
    }

    def __init__(self, categories=None, *args, **kwargs):
        super(NaverCategorySpider, self).__init__(*args, **kwargs)
        self.categories = categories
        self.accumulater = 0


    def start_requests(self):
        if self.categories:
            urls = map(lambda x: "https://search.shopping.naver.com/category/category.nhn?cat_id={0}".format(x)
                       , self.categories.split(','))
            cb_kwargs = {'pre_categories': {}}
            for url in urls:
                yield scrapy.Request(url=url, callback=self.parse_categories,
                                     cb_kwargs=cb_kwargs,
                                     # headers={'User-Agent': str(ua.chrome)}
                                     )
        else:
            urls = [
                'https://shopping.naver.com/'
            ]

            cb_kwargs = {}
            for url in urls:
                yield scrapy.Request(url=url,
                                     callback=self.get_first_depth,
                                     cb_kwargs=cb_kwargs,
                                     )

    def get_first_depth(self, response, **cb_kwargs):
        container = response.css('li._category_area_li a')


    def parse_categories(self, response, **cb_kwargs):
        cont = response.xpath('//*[@id="__next"]/div/div[2]/div')

        url_pattern = r'^(\/search\/category\?catId=)'
        p = re.compile(url_pattern)
        urls = []

        for a in cont.css('a'):
            a_href = a.attrib['href']
            a_text = a.css('a::text').get()

            m = p.match(a_href)
            if m:
                # print('url :', a_href, '/ name : ', a_text)
                # catId=50000167&pagingIndex=1&pagingSize=80&productSet=total
                urls.append(a_href + '&pagingIndex=1&pagingSize=80&productSet=total')

        print('total categories: ', len(urls))
        for i, url in enumerate(urls, 1):
            if i > 1: break

            yield response.follow(url,
                                  callback=self.parse_categories_details,
                                  cb_kwargs=cb_kwargs,
                                  )

    def parse_categories_details(self, response, **cb_kwargs):
        print('called')
        print('current url : ', response.request.url)
        dt = json.loads(response.css("#__NEXT_DATA__::text").get())
        prd = dt["props"]['pageProps']['initialState']['products']['list']
        id_list = list(map(lambda x: x['item']['id'], prd))
        zzim_param = ",".join(id_list)
        zzim_dict = {}
        parts = urlparse(response.request.url)
        cate_id = dict(parse_qsl(urlsplit(parts.query).path)).get('catId', None)

        print('total number of items on this page: ', len(prd))

        try:
            ajx_res = requests.get(ZZIM_API_URL, params={'nvMid': zzim_param}, headers={'urlprefix': '/api'})
            zzim_dict.update(ajx_res.json()['zzim'])
        except Exception as e:
            print(e)

        for item in prd:
            if self.accumulater > NUM_OF_ITEMS_PER_CATE: break
            try:
                il = ItemLoader(item=NaverCategoryItem())
                product_dict = item['item']

                # 광고상품 건너 뛰기
                if product_dict.get('adId', None):
                    continue
                zzim_cnt = zzim_dict[product_dict['id']]['count']

                il.add_value('cate_id', cate_id)
                il.add_value('rnk', product_dict.get('rank', None))
                il.add_value('nv_mid', product_dict.get('id', None))

                il.add_value('single_mall_nm', product_dict.get('mallName', None))
                il.add_value('item_url', product_dict.get('adcrUrl', None) or product_dict.get('crUrl', None))
                il.add_value('rate', product_dict.get('scoreInfo', None))
                il.add_value('item_nm', product_dict.get('productName', None))
                il.add_value('min_price', product_dict.get('lowPrice', None))
                il.add_value('max_price', product_dict.get('highPrice', None))
                il.add_value('reg_date', product_dict.get('lnchYm', None) or product_dict.get('openDate', None))
                il.add_value('wish_cnt', zzim_cnt)
                il.add_value('seller_cnt', product_dict.get('mallCount', None))
                il.add_value('review_cnt', product_dict.get('reviewCountSum', None))
                il.add_value('image_url', product_dict.get('imageUrl', None))
                il.add_value('fixeddate', 'date')
                il.add_value('type', 'nvshop_category_item')

                yield il.load_item()
            except Exception as e:
                print('err: ', e, 'at rank', item['item'].get('rank', None), ': ', item['item']['productName'])
            else:
                self.accumulater += 1
            finally:
                # print(il.load_item())
                # print(item['item'])
                pass



        print('current accum: ', self.accumulater)
        # if self.accumulater <= NUM_OF_ITEMS_PER_CATE:
        #     parts = urlparse(response.request.url)
        #     qs = dict(parse_qsl(parts.query))
        #     next_url = qs_replace(response.request.url,
        #                           'pagingIndex',
        #                           int(qs['pagingIndex']) + 1)
        #
        #     yield response.follow(next_url,
        #                           callback=self.parse_categories_details,
        #                           cb_kwargs=cb_kwargs,
        #                           )


        # yield response.follow(url,
        #                       callback=self.parse_categories_details,
        #                       cb_kwargs=cb_kwargs,
        #                       )

        # for key, value in prd[4]['item'].items():
        #     print('{}: {}'.format(key, value))


        # print(response.text)

        # arr = response.css('#__next > div > div.container > div li[class^=basicList_item]')
        # print("arr:  ", len(arr))








