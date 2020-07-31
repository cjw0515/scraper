import scrapy
from scrapy.loader import ItemLoader
from scrapy.selector import Selector
from ..items import BestItems1300k
import logging
from global_settings import BOT_NAME
from collections import OrderedDict
from utils.utils import get_page_data, qs_replace, get_qs
from fake_useragent import UserAgent
import json

import requests

ua = UserAgent()
RUNNING_BOT = 5
DETAIL_URL = 'https://www.1300k.com/shop/goodsDetailAjax.html?f_goodsno=215024441783'
CATEGORY_URL = 'https://www.1300k.com/shop/best/bestAjax.html'

class BestItem1300k(scrapy.Spider):
    name = "1300k_best_item"

    custom_settings = {
        'ITEM_PIPELINES': {
            'lightweight_scrap.pipelines.LightweightScrapPipeline': 300,
        },
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        'PIPELINE_CONF': [{
            'total_line': 1,
            'del_line_num': 6000,
            'file': None,
            'file_name': '1300k_best_item-{0}.csv'.format(BOT_NAME),
            'exporter': None,
            'fields_to_export': ['rnk', 'cate', 'item_nm', 'price', 'sale_price', 'item_code', 'brand',
                                 'image_url', 'review_cnt', 'like_cnt', 'fixeddate', 'type'],
            'is_upload': True,
            'op_stat': True,
            's3_group': name
        }]
    }
    def __init__(self, page=None, chain=1, *args, **kwargs):
        super(BestItem1300k, self).__init__(*args, **kwargs)
        self.page = int(page) if page else 1
        self.use_crawl_chain = chain

    def start_requests(self):
        urls = [
            'https://www.1300k.com/shop/best/best.html',
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **cb_kwargs):
        lis = response.css('#category > div > div > ul > li')
        lis = get_page_data(lis, RUNNING_BOT, self.page)
        for idx, li in enumerate(lis, 1):
            cno = li.css('a::attr(cno)').getall()
            current_category = li.css('a > span.txt::text').get()
            args = {
                'current_category': current_category
            }
            payload = {
                'mode': 'BEST',
                'cno': cno
            }
            yield scrapy.FormRequest(
                url=CATEGORY_URL,
                formdata=payload,
                callback=self.parse_top100,
                cb_kwargs=args,
                method='POST'
            )

    def parse_top100(self, response, **cb_kwargs):
        html = Selector(text=json.loads(response.text)['html'])
        item_links = html.css('li a::attr(href)').getall()

        for rnk, link in enumerate(item_links, 1):
            # if rnk != 1: break # test
            item_code = get_qs(link).get('f_goodsno', '')
            ajax_url = qs_replace(DETAIL_URL, 'f_goodsno', item_code)
            item_kwargs = {
                'rnk': rnk,
                'cate': cb_kwargs.get('current_category', ''),
                'item_code': item_code,
                'ajax_url': ajax_url
            }

            yield response.follow(link,
                                  callback=self.parse_details,
                                  cb_kwargs=item_kwargs,
                                  )

    def parse_details(self, response, **cb_kwargs):
        ajax_res = requests.get(cb_kwargs.get('ajax_url'), headers={'User-Agent': str(ua.chrome)})
        html = ajax_res.json()['strSmryHtml']
        s = Selector(text=html)

        item_nm = s.css('div.smry_tit > div.gds_nmbx > h2::text').get()
        price = s.css('div.smry_rgt > table.info_box em.price_s::text').get()
        sale_price = s.css('div.smry_rgt > table.info_box em.price_r::text').get() or \
                     s.css('div.smry_rgt > table.info_box em.price_b::text').get()
        brand = s.css('div.smry_tit > div.smry_brand > a > em.brnm_kor::text').get()
        image_url = s.css('div.smry_lft > div > ul.mpic > li:nth-child(1) > img::attr(src)').get()
        review_cnt = response.css('#gdt_nav_ps > li.k_gdt3.gdt3_navtab2_on.txt_ps > em::text').get()
        like_cnt = s.css('#idGoodsFavorCnt::text').get()

        il = ItemLoader(item=BestItems1300k())

        il.add_value('rnk', cb_kwargs.get('rnk', 0))
        il.add_value('cate', cb_kwargs.get('cate', ''))
        il.add_value('item_nm', item_nm)
        il.add_value('price', price)
        il.add_value('sale_price', sale_price)
        il.add_value('item_code', cb_kwargs.get('item_code', ''))
        il.add_value('brand', brand)
        il.add_value('image_url', image_url)
        il.add_value('review_cnt', review_cnt)
        il.add_value('like_cnt', like_cnt)
        il.add_value('fixeddate', "date")
        il.add_value('type', self.name)

        yield il.load_item()

