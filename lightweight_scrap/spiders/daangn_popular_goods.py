import scrapy
from scrapy.loader import ItemLoader
from ..items import DaangnPopItems
import logging
from global_settings import BOT_NAME
from urllib.parse import urljoin
from utils.utils import get_page_data

BASE_URL = "https://www.daangn.com/region/"
RUNNING_BOT = 5
depth_limit = 3

def extrace_int(val):
    return int(''.join(i for i in val if i.isdigit()) or 0)

def getPath(p1=None, p2=None, p3=None):
    return (p1 or '') + ('/{}'.format(p2) if p2 else '') + ('/{}'.format(p3) if p3 else '')

class DaangnPopGoodsSpider(scrapy.Spider):
    # 스파이더의 식별자. 프로젝트 내에서 유일해야한다.
    name = "daangn_popular_goods"

    custom_settings = {
        'ITEM_PIPELINES': {
            'lightweight_scrap.pipelines.LightweightScrapPipeline': 300,
        },
        'PIPELINE_CONF': [{
            'total_line': 1,
            'del_line_num': 6000,
            'file': None,
            'file_name': 'daangn_pop_goods-{0}.csv'.format(BOT_NAME),
            'exporter': None,
            'fields_to_export': ['title', 'cate', 'price', 'interest', 'chat', 'view'
                , 'region1', 'region2', 'region3', 'fixeddate', 'type'],
            'is_upload': True,
            'op_stat': True,
            's3_group': name
        }]
    }

    def __init__(self, page=None, *args, **kwargs):
        super(DaangnPopGoodsSpider, self).__init__(*args, **kwargs)
        self.page = int(page) if page else 1
    # 스파이더가 크롤링을 시작할 반복 요청 (요청 목록을 반환하거나 생성기 함수를 작성할 수 있음)을 반환해야합니다. 후속 요청은 이러한 초기 요청에서 연속적으로 생성됩니다.
    def start_requests(self):
        urls = [
            'https://www.daangn.com/hot_articles',
        ]
        # 함수 안에서 yield를 사용하면 함수는 제너레이터가 되며 yield에는 값을 지정한다.
        for url in urls:
            yield scrapy.Request(url=url, callback=self.req_deth)

    def parse(self, response, **cb_kwargs):
        try:
            il = ItemLoader(item=DaangnPopItems())

            title = response.css('#article-title::text').get()
            cate = response.css('#article-category::text').get().strip().replace(" ∙", "")
            price = extrace_int(response.css('#article-price::text').get() or '0')
            info_arr = response.css('#article-counts::text').get().strip().split(' ∙ ')
            interest = extrace_int(info_arr[0])
            chat = extrace_int(info_arr[1])
            view = extrace_int(info_arr[2])
            fixeddate = "date"
            type = self.name

            il.add_value('title', title)
            il.add_value('cate', cate)
            il.add_value('price', price)
            il.add_value('interest', interest)
            il.add_value('chat', chat)
            il.add_value('view', view)
            il.add_value('region1', cb_kwargs.get('depth1', ''))
            il.add_value('region2', cb_kwargs.get('depth2', ''))
            il.add_value('region3', cb_kwargs.get('depth3', ''))
            il.add_value('fixeddate', fixeddate)
            il.add_value('type', type)

            yield il.load_item()
        except Exception as e:
            logging.log(logging.ERROR, e + ' / ' +response.css('#article-title::text').get())

    def req_deth(self, response, **cb_kwargs):
        cb_kwargs.update({'for_depth': cb_kwargs.get('for_depth', 0) + 1})

        a = response.css('#content > section.cards-wrap > article > a::attr(href)').getall()
        for link in a:
            yield response.follow(link,
                                  callback=self.parse,
                                  cb_kwargs=cb_kwargs,
                                  )

        if cb_kwargs['for_depth'] > depth_limit: return False

        reg_arr = [x for x in response.css('#region{} > option::attr(value)'.format(cb_kwargs['for_depth'])).getall() if x]
        reg_arr = get_page_data(reg_arr, RUNNING_BOT, self.page) if cb_kwargs.get('for_depth') == 1 else reg_arr

        for d in reg_arr:
            d1 = d if cb_kwargs.get('for_depth') == 1 else cb_kwargs.get('depth1', None)
            d2 = d if cb_kwargs.get('for_depth') == 2 else cb_kwargs.get('depth2', None)
            d3 = d if cb_kwargs.get('for_depth') == 3 else cb_kwargs.get('depth3', None)

            url = urljoin(BASE_URL, getPath(d1, d2, d3))
            logging.log(logging.INFO, 'url : ' + url)
            cb_kwargs.update({
                'depth1': d1,
                'depth2': d2,
                'depth3': d3,
            })

            yield response.follow(url,
                                 callback=self.req_deth,
                                 cb_kwargs=cb_kwargs,
                                 )