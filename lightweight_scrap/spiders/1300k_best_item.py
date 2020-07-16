import scrapy
from scrapy.loader import ItemLoader
from ..items import DaangnRnkKwd
import logging
from global_settings import BOT_NAME
from collections import OrderedDict
from utils.utils import get_page_data

RUNNING_BOT = 5

class BestItem1300k(scrapy.Spider):
    name = "1300k_best_item"

    custom_settings = {
        'ITEM_PIPELINES': {
            'lightweight_scrap.pipelines.LightweightScrapPipeline': 300,
        },
        'PIPELINE_CONF': [{
            'total_line': 1,
            'del_line_num': 6000,
            'file': None,
            'file_name': '1300k_best_item-{0}.csv'.format(BOT_NAME),
            'exporter': None,
            'fields_to_export': ['rnk', 'kwd', 'indecrease', 'fixeddate', 'type'],
            'is_upload': False,
            'op_stat': False,
            's3_group': name
        }]
    }
    def __init__(self, page=None, *args, **kwargs):
        super(BestItem1300k, self).__init__(*args, **kwargs)
        self.page = int(page) if page else 1

    def start_requests(self):
        urls = [
            'https://www.1300k.com/shop/best/best.html',
        ]

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **cb_kwargs):
        if cb_kwargs.get('for_depth', 0) == 0:
            category_links = response.xpath('//*[@id="idSpeCateList"]'
                                            '//a[re:test(@href, "\/shop\/best\/best.html")]'
                                            '//@href').getall()
            print(category_links)
            category_links = get_page_data(category_links, RUNNING_BOT, 4)

            for category in category_links:
                cb_kwargs.update({'for_depth': 1})
                print(category)
                yield response.follow(category,
                                      callback=self.parse,
                                      cb_kwargs=cb_kwargs,
                                      )

        if cb_kwargs.get('for_depth', 0) == 1:
            current_category = response.css("#idSpeCateList > ul > li.cate_on > a::text").get()
            item_link = response.xpath('//*[@id="container"]'
                                       '//a[re:test(@href, "\/shop\/goodsDetail.html\?f_goodsno=")]'
                                       '//@href').getall()
            item_link = list(OrderedDict((item, None) for item in item_link))
            print(current_category)
            # for rnk, link in enumerate(item_link, 1):
            #     item_kwargs = {
            #         'rnk': rnk,
            #         'cate': current_category
            #     }
            #     yield response.follow(link,
            #                           callback=self.parse_details,
            #                           cb_kwargs=item_kwargs,
            #                           )

    def parse_details(self, response, **cb_kwargs):
        print(response)

        # rnk_li = response.css('#top-keywords-list li')
        # for idx, item in enumerate(rnk_li, 1):
        #     try:
        #         il = ItemLoader(item=DaangnRnkKwd())
        #
        #         kwd = item.css(".keyword-text::text").get()
        #         indecrease = int(item.css(".rank .changed_rank::text").get() or 0)
        #         fixeddate = "date"
        #         type = self.name
        #
        #         if item.css(".rank .down"):
        #             indecrease *= -1
        #
        #         il.add_value('rnk', idx)
        #         il.add_value('kwd', kwd)
        #         il.add_value('indecrease', indecrease)
        #         il.add_value('fixeddate', fixeddate)
        #         il.add_value('type', type)
        #
        #         yield il.load_item()
        #     except Exception as e:
        #         logging.log(logging.ERROR, 'error parsing daangn_kwd_rank : ' + e)