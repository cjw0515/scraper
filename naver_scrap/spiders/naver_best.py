# -*- coding: utf-8 -*-
import sys, os

sys.path.append("C:/anaconda3/envs/scraper-10x10/Lib/site-packages")
import scrapy
from scrapy.loader import ItemLoader
from ..items import NaverBestItem, NaverBestKeyword, NaverBestBrand
from urllib.parse import urlparse, parse_qs, parse_qsl, urlencode, urlunparse
import logging
from datetime import datetime
'''
    depth 제한 
    최대 4 최소 1    
'''

# 인기 검색어 / 브랜드 request url
best_keyword_url = 'https://search.shopping.naver.com/best100v2/detail/kwd.nhn'

category_depth_allow = 1
crawl_item = True
crawl_keyword = True
crawl_brand = True

if os.environ['ENV'] == 'prod':
    category_depth_allow = 3
    crawl_item = True
    crawl_keyword = True
    crawl_brand = True


def set_best_keyword_url(url, query):
    parts = urlparse(url)
    qs = dict(parse_qsl(parts.query))
    qs.update(query)
    parts = parts._replace(query=urlencode(qs))
    new_url = urlunparse(parts)

    return new_url


'''
주제 :
nvshop_best_item    : 베스트 상품 100
nvshop_best_keyword : 베스트 키워드
nvshop_best_brand   : 베스트 브랜드
'''


class NaverBestCategorySpider(scrapy.Spider):
    name = 'naver_best_category'
    custom_settings = {
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_START_DELAY': 5,
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
        'DOWNLOAD_DELAY': 0.5,
        'ITEM_PIPELINES': {
            'naver_scrap.pipelines.NaverScrapPipeline': 300,
        },
        'SPIDER_MIDDLEWARES': {
            'naver_scrap.middlewares.NaverScrapSpiderMiddleware': 543,
        },
        'DOWNLOADER_MIDDLEWARES': {
            'naver_scrap.middlewares.NaverScrapDownloaderMiddleware': 543,
            'naver_scrap.middlewares.SleepRetryMiddleware': 100,
        },
        # 크롤링 여부
        'CRAWL_ITEM': crawl_item,
        'CRAWL_KEYWORD': crawl_keyword,
        'CRAWL_BRAND': crawl_brand,
    }

    def __init__(self, categories=None, chain=1, depth=None, *args, **kwargs):
        super(NaverBestCategorySpider, self).__init__(*args, **kwargs)
        self.category_depth_allow = int(depth) if depth else int(category_depth_allow)
        self.categories = categories
        self.use_crawl_chain = chain

    def parse_first_depth(self, response):
        """
            1depth 카테고리 파싱
        """
        '''
            카테고리 파싱 첫번째 방법
        '''
        container = response.css('li._category_area_li a')
        for li in container:
            link = li.css('a::attr(href)').get()
            cb_kwargs = {'pre_categories': {}}

            yield response.follow(link,
                                  callback=self.parse_morethan_second_depth,
                                  cb_kwargs=cb_kwargs,
                                  # headers={'User-Agent': str(ua.chrome)}
                                  )
        '''
            두번째 방법
        '''
        # yield from response.follow_all(links, callback=self.parse_second_depth)

    def start_requests(self):
        if self.categories:
            urls = map(lambda x: "https://search.shopping.naver.com/best100v2/detail.nhn?catId={0}".format(x)
                       , self.categories.split(','))
            cb_kwargs = {'pre_categories': {}}
            for url in urls:
                yield scrapy.Request(url=url, callback=self.parse_morethan_second_depth,
                                     cb_kwargs=cb_kwargs,
                                     # headers={'User-Agent': str(ua.chrome)}
                                     )
        else:
            urls = [
                'https://search.shopping.naver.com/best100v2/main.nhn'
            ]
            # yield scrapy.Request(url="http://httpbin.org/ip", callback=self.chk_ip)
            for url in urls:
                yield scrapy.Request(url=url, callback=self.parse_first_depth)

    def parse_best_100_in_detail(self, response, **cb_kwargs):
        def get_age_grades(charts, grade):
            age = ''
            for c in charts:
                c_g = c.css('div.vertical_bar > div > span.grade::text').get()
                if c_g is not None and str(grade) == str(c_g):
                    age = c.css('div.label::text').get()
                    break
            return age

        def get_goods_info(goods_info, info_key):
            res = ''
            for info in goods_info:
                try:
                    key = info.css('span::text').get().strip()
                    if key == info_key:
                        res = info.css('em::text').get()
                        break
                except Exception as e:
                    pass

            return res

        def get_single_mall_name(top_mall_list):
            if len(top_mall_list) == 1:
                return top_mall_list[0].css('td.mall_area > div > span.mall > a::text').get().strip() or ''

            # _mainSummaryPrice > table > tbody > tr:nth-child(2) > td.mall_area > div > span.mall_cell > span

        chart = response.css('#bar-container > ul > li')
        goods_info = response.css('#container div.goods_info div.info_inner span')
        top_mall_list = response.css('#_mainSummaryPrice > table > tbody > tr')
        sf = response.css('#_mainSummaryPrice > table > tbody > tr .sico_npay_plus')
        item_details = {}
        # 데이터 구분값
        try:
            item_details.update({
                'seller_cnt': response.css('#snb > ul > li.mall_place.on > a > em::text').get(),
                'single_mall_nm': get_single_mall_name(top_mall_list),
                'rate': response.css('#container > div.summary_area > div.summary_info.'
                                     '_itemSection > div > div.h_area > div > div.gpa::text').get(),
                'prefer_age1': get_age_grades(chart, 1),
                'prefer_age2': get_age_grades(chart, 2),
                'female_rate': response.css(
                    '#modelDemographyGraph > div.chart_area > div.gender._gender::attr(data-f)').get(),
                'min_price': response.css('#content > div > div.summary_cet > div.price_area > span > em::text').get(),
                'manufacturer': get_goods_info(goods_info, '제조사'),
                'brand': get_goods_info(goods_info, '브랜드'),
                'reg_date': get_goods_info(goods_info, '등록일').replace(".", "-") + "01",
                'wish_cnt': response.css('#jjim > em.cnt._keepCount::text').get(),
                'review_cnt': response.css('#snb > ul > li.mall_review > a > em::text').get(),
                'storefarm_num': len(sf),
                'top_store_num': len(top_mall_list)
            })
        except Exception as e:
            print('error msg: ', e)
            logging.log(logging.ERROR, (cb_kwargs['item_nm']))

        item_details.update(cb_kwargs)
        item_details.update({'type': 'nvshop_best_item'})

        try:
            logging.log(logging.INFO,
                        'depth :[{0}] / 카테고리 :'.format(cb_kwargs['depth']) + cb_kwargs['cate_name'] + '/ 이름: '
                        + item_details['item_nm'])
        except Exception as e:
            print('no cate_name')

        il = ItemLoader(item=NaverBestItem())
        for key, value in item_details.items():
            il.add_value(key, value)

        yield il.load_item()
        return

    def chk_ip(self, response):
        print(response.text)

    def parse_best_keyword(self, response, **cb_kwargs):
        rnk_list = response.css('#popular_srch_lst > li')

        for rnk in rnk_list:
            rnk_flg = rnk.css('span.vary span::text').get().strip()
            elev_width = int(rnk.css('span.vary::text')[1].get().strip() or 0)

            keyword_data = {
                'rnk': rnk.css('em::text').get()[:-1],
                'keyword': rnk.css('span.txt a::attr(title)').get().strip(),
                'trend': elev_width if rnk_flg == '상승' else elev_width * -1 if rnk_flg == '하락' else 0,
                'fixeddate': datetime.now().strftime("%Y-%m-%d %X"),
            }
            keyword_data.update(cb_kwargs)

            il = ItemLoader(item=NaverBestKeyword())
            for key, value in keyword_data.items():
                il.add_value(key, value)

            logging.log(logging.INFO, keyword_data)

            yield il.load_item()

    def parse_best_brand(self, response, **cb_kwargs):
        rnk_list = response.css('#popular_srch_lst > li')

        for rnk in rnk_list:
            rnk_flg = rnk.css('span.vary span::text').get().strip()
            elev_width = int(rnk.css('span.vary::text')[1].get().strip() or 0)

            brand_data = {
                'rnk': rnk.css('em::text').get()[:-1],
                'keyword': rnk.css('span.txt a::attr(title)').get().strip(),
                'trend': elev_width if rnk_flg == '상승' else elev_width * -1 if rnk_flg == '하락' else 0,
                'fixeddate': datetime.now().strftime("%Y-%m-%d %X"),
            }
            brand_data.update(cb_kwargs)

            il = ItemLoader(item=NaverBestBrand())
            for key, value in brand_data.items():
                il.add_value(key, value)

            logging.log(logging.INFO, brand_data)

            yield il.load_item()

    def parse_morethan_second_depth(self, response, **cb_kwargs):
        """
            2depth 이상 카테고리 파싱
        """
        # print(cb_kwargs)
        # print('requests headers: ', response.request.headers)
        depth = len(response.css('#content > div.category_lst > div.summary_area > div > span'))
        pre_categories = cb_kwargs['pre_categories'] or {}
        cate_id = parse_qs(urlparse(response.request.url).query)['catId'][0]
        cate_name = response.css('#content > div.category_lst > div.summary_area > div > a.on::text').get()
        current_categories = sorted(
            list(
                filter(lambda x: x != '', map(lambda x: x.strip(),
                                              response.css('div[id=srh_category1] ul li a em::text').getall() or [])
                       )
            )
        )
        logging.log(logging.INFO, '=============================== depth: [{0}]'
                    .format(depth) + ',cate_name: ' + cate_name + ': '
                    + response.request.url + ' ===============================')
        # print('pre categories: ', pre_categories)
        # print('current categories: ', current_categories)
        """
            best100 상품 파싱            
        """
        if crawl_item:
            best_100 = response.css('div[id=productListArea] ul li')
            for idx, item in enumerate(best_100, start=1):
                detail_args = {
                    'image_url': item.css('.thumb_area a img::attr(data-original)').get(),
                    'cate_id': cate_id,
                    'rnk': idx,  # item.css('.thumb_area div.best_rnk em::text').get(),
                    'nv_mid': item.attrib['data-nv-mid'],
                    'item_url': "https://search.shopping.naver.com/detail/lite.nhn?cat_id={0}&nv_mid={1}"
                                .format(cate_id, item.attrib['data-nv-mid']),
                    'item_nm': item.css('p > a::attr(title)').get(),
                    'cate_name': cate_name,
                    'depth': depth,
                }
                if len(item.css('div.info > span > a.btn_price_comp')) == 0:
                    details = {
                        'seller_cnt': '',
                        'single_mall_nm': '',
                        'rate': '',
                        'prefer_age1': '',
                        'prefer_age2': '',
                        'female_rate': '',
                        'min_price': '',
                        'manufacturer': '',
                        'brand': '',
                        'reg_date': '',
                        'wish_cnt': '',
                        'review_cnt': '',
                        'storefarm_num': 0,
                        'top_store_num': 0,
                    }
                    details.update({'type': 'nvshop_best_item'})
                    details.update(detail_args)
                    logging.log(logging.INFO, '카테고리 :' + cate_name + '/ 이름: ' + details['item_nm'])

                    il = ItemLoader(item=NaverBestItem())
                    for key, value in details.items():
                        il.add_value(key, value)

                    yield il.load_item()
                else:
                    yield response.follow(detail_args['item_url'],
                                          callback=self.parse_best_100_in_detail,
                                          cb_kwargs=detail_args,
                                          # headers={'User-Agent': str(ua.chrome)}
                                          )

        """
            인기 검색어 파싱, 인기 브랜드 파싱            
        """
        # https://search.shopping.naver.com/best100v2/detail/kwd.nhn?catId=50001376&kwdType=KWD&dateType=week&startDate=2020.05.29&endDate=2020.06.04
        req_params = [
            # 인기검색어
            {
                'catId': cate_id,
                'kwdType': 'KWD',
                'dateType': 'today',
            },
            {
                'catId': cate_id,
                'kwdType': 'KWD',
                'dateType': 'week',
            },
            # 인기 브랜드
            {
                'catId': cate_id,
                'kwdType': 'BRD',
                'dateType': 'today',
            },
            {
                'catId': cate_id,
                'kwdType': 'BRD',
                'dateType': 'week',
            },
        ]

        for best_kb_params in req_params:
            keyword_args = {
                'cate_id': cate_id,
                'period': 'daily' if best_kb_params['dateType'] == 'today' else 'weekly',
                'gb': 'keyword' if best_kb_params['kwdType'] == 'KWD' else 'brand',
                'type': 'nvshop_best_keyword' if best_kb_params['kwdType'] == 'KWD' else 'nvshop_best_brand',
            }
            tmp_url = set_best_keyword_url(best_keyword_url, query=best_kb_params)
            if crawl_keyword and best_kb_params['kwdType'] == 'KWD':
                yield scrapy.Request(url=tmp_url, callback=self.parse_best_keyword,
                                     cb_kwargs=keyword_args,
                                     # headers={'User-Agent': str(ua.chrome)}
                                     )
            if crawl_brand and best_kb_params['kwdType'] == 'BRD':
                yield scrapy.Request(url=tmp_url, callback=self.parse_best_brand,
                                     cb_kwargs=keyword_args,
                                     # headers={'User-Agent': str(ua.chrome)}
                                     )

        if depth >= self.category_depth_allow:
            return

        """
            카테고리 체인 파싱 max 4depth 
            ** recursive
        """
        if pre_categories != current_categories:
            container = response.css('div[id=srh_category1] ul li a')
            for a in container:
                link = a.attrib['href']
                cb_kwargs = {'pre_categories': current_categories}

                yield response.follow(link,
                                      callback=self.parse_morethan_second_depth,
                                      cb_kwargs=cb_kwargs,
                                      # headers={'User-Agent': str(ua.chrome)}
                                      )
