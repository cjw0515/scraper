import scrapy
from scrapy.utils.project import get_project_settings
from scrapy.loader import ItemLoader
from ..items import DaangnRnkKwd
import logging
from global_settings import BOT_NAME

class DaangnKwdRank(scrapy.Spider):
    # 스파이더의 식별자. 프로젝트 내에서 유일해야한다.
    name = "daangn_kwd_rank"

    custom_settings = {
        'ITEM_PIPELINES': {
            'lightweight_scrap.pipelines.LightweightScrapPipeline': 300,
        },
        'PIPELINE_CONF': [{
            'total_line': 1,
            'del_line_num': 6000,
            'file': None,
            'file_name': 'daangn_rnk-{0}.csv'.format(BOT_NAME),
            'exporter': None,
            'fields_to_export': ['rnk', 'kwd', 'indecrease', 'fixeddate', 'type'],
            'is_upload': True,
            'op_stat': True,
            's3_group': name
        }]
    }
    # 스파이더가 크롤링을 시작할 반복 요청 (요청 목록을 반환하거나 생성기 함수를 작성할 수 있음)을 반환해야합니다. 후속 요청은 이러한 초기 요청에서 연속적으로 생성됩니다.
    def start_requests(self):
        urls = [
            'https://www.daangn.com/top_keywords',
        ]
        # 함수 안에서 yield를 사용하면 함수는 제너레이터가 되며 yield에는 값을 지정한다.
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    # 각 요청에 대해 다운로드 된 응답을 처리하기 위해 호출되는 메소드
    def parse(self, response):
        rnk_li = response.css('#top-keywords-list li')
        for idx, item in enumerate(rnk_li, 1):
            try:
                il = ItemLoader(item=DaangnRnkKwd())

                kwd = item.css(".keyword-text::text").get()
                indecrease = int(item.css(".rank .changed_rank::text").get() or 0)
                fixeddate = "date"
                type = self.name

                if item.css(".rank .down"):
                    indecrease *= -1

                il.add_value('rnk', idx)
                il.add_value('kwd', kwd)
                il.add_value('indecrease', indecrease)
                il.add_value('fixeddate', fixeddate)
                il.add_value('type', type)

                yield il.load_item()
            except Exception as e:
                logging.log(logging.ERROR, 'error parsing daangn_kwd_rank : ' + e)