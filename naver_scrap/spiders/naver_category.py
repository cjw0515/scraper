# -*- coding: utf-8 -*-
import sys, os

sys.path.append("C:/anaconda3/envs/scraper-10x10/Lib/site-packages")
import scrapy
from scrapy.selector import Selector
from scrapy.loader import ItemLoader
from ..items import NaverCategoryItem
from fake_useragent import UserAgent
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse, urlsplit
import logging
import requests
from utils.utils import get_page_data

import re
import json

ua = UserAgent()
ZZIM_API_URL = "https://search.shopping.naver.com/product-zzim/products"
NUM_OF_ITEMS_PER_CATE = 1000
FIRST_CATEGORIES = [50000000, 50000001, 50000007, 50000009, 50000003,
                    50000004, 50000005, 50000006, 50000002, 50000010, 50000008]

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

    def __init__(self, page=None, *args, **kwargs):
        super(NaverCategorySpider, self).__init__(*args, **kwargs)
        self.page = int(page) if page else 1

    def start_requests(self):
        all_cate = []
        first_cate_urls = map(lambda x: "https://search.shopping.naver.com/category/category.nhn?cat_id={0}".format(x)
                   , FIRST_CATEGORIES)
        for url in first_cate_urls:
            res = requests.get(url)
            html = Selector(text=res.text)
            cont = html.xpath('//*[@id="__next"]/div/div[2]/div')

            url_pattern = r'^(\/search\/category\?catId=)'
            p = re.compile(url_pattern)

            for a in cont.css('a'):
                a_href = a.attrib['href']
                a_text = a.css('a::text').get()

                m = p.match(a_href)
                if m:
                    all_cate.append('https://search.shopping.naver.com' +
                                    a_href +
                                    '&pagingIndex=1&pagingSize=80&productSet=total')

        all_cate = list(set(all_cate))

        all_cate = get_page_data(all_cate, 5, self.page)
        for url in all_cate:
            param = {'accumulater': 0, 'pre_page_prd_list': []}
            yield scrapy.Request(url=url,
                                 callback=self.parse_categories_details,
                                 cb_kwargs=param,
                                 # headers={'User-Agent': str(ua.chrome)}
                                 )

    def parse_categories_details(self, response, **cb_kwargs):
        logging.log(logging.INFO, 'current url : ' + response.request.url)
        dt = json.loads(response.css("#__NEXT_DATA__::text").get())
        prd = dt["props"]['pageProps']['initialState']['products']['list']
        # 상품 없을 시 유효한 카테고리가 아님.
        if len(prd) == 0: return

        id_list = list(map(lambda x: x['item']['id'], prd))
        # 상위 6개 id리스트 비교하고 같으면 더이상 다음 페이지가 없는것으로 판단함.
        if cb_kwargs['pre_page_prd_list'][4:10] == id_list[4:10]: return

        # 찜 개수 api 호출
        zzim_param = ",".join(id_list)
        zzim_dict = {}
        parts = urlparse(response.request.url)
        cate_id = dict(parse_qsl(urlsplit(parts.query).path)).get('catId', None)

        local_accum = cb_kwargs['accumulater']
        try:
            ajx_res = requests.get(ZZIM_API_URL, params={'nvMid': zzim_param}, headers={'urlprefix': '/api'})
            zzim_dict.update(ajx_res.json()['zzim'])
        except Exception as e:
            logging.log(logging.ERROR, 'error sending ajax request : ' + e)

        for item in prd:
            if local_accum > NUM_OF_ITEMS_PER_CATE: break
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

                local_accum += 1

                yield il.load_item()
            except Exception as e:
                logging.log(logging.ERROR, 'err: {} at rank : {} - name: {}'.format(e,
                                                               item['item'].get('rank', None),
                                                               item['item']['productName']))
            finally:
                # print(il.load_item())
                # print(item['item'])
                pass

        if local_accum <= NUM_OF_ITEMS_PER_CATE:
            parts = urlparse(response.request.url)
            qs = dict(parse_qsl(parts.query))
            next_url = qs_replace(response.request.url,
                                  'pagingIndex',
                                  int(qs['pagingIndex']) + 1)
            cb_kwargs.update({'accumulater': local_accum, 'pre_page_prd_list': id_list})

            yield response.follow(next_url,
                                  callback=self.parse_categories_details,
                                  cb_kwargs=cb_kwargs,
                                  )

        # for key, value in prd[4]['item'].items():
        #     print('{}: {}'.format(key, value))








