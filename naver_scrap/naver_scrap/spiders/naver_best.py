# -*- coding: utf-8 -*-
import sys
sys.path.append("C:/anaconda3/envs/scraper-10x10/Lib/site-packages")
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from fake_useragent import UserAgent
from urllib.parse import urlparse, parse_qs,parse_qsl , urlencode, urlunparse
import logging
from datetime import datetime

ua = UserAgent()
'''
    depth 제한 
    최대 4 최소 2    
'''
category_depth_setting = 2
log_level = 'INFO'
category_test_link = 'https://search.shopping.naver.com/best100v2/detail.nhn?catId=50000000'
# category_test_link = ''
# 인기 검색어 / 브랜드 request url
best_keyword_url = 'https://search.shopping.naver.com/best100v2/detail/kwd.nhn'

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
        'LOG_LEVEL': log_level,
        'ITEM_PIPELINES': {
            'naver_scrap.pipelines.NaverScrapPipeline': 300,
        },
        # 크롤링 여부
        'CRAWL_ITEM': crawl_item,
        'CRAWL_KEYWORD': crawl_keyword,
        'CRAWL_BRAND': crawl_brand,
    }

    def __init__(self, category=None, *args, **kwargs):
        super(NaverBestCategorySpider, self).__init__(*args, **kwargs)
        self.category_depth_setting = category_depth_setting

    def start_requests(self):
        if not category_test_link:
            urls = [
                'https://search.shopping.naver.com/best100v2/main.nhn'
            ]
            # yield scrapy.Request(url="http://httpbin.org/ip", callback=self.chk_ip)
            for url in urls:
                yield scrapy.Request(url=url, callback=self.parse_first_depth)
        '''    
        urls = [
            'https://search.shopping.naver.com/detail/detail.nhn?cat_id=50002170&nv_mid=20811239770&NaPm=ct%3Dkb0e7u80%7Cci%3D1999b2bad27c658327cfac0541fcc1e1ab185c7d%7Ctr%3Dsl%7Csn%3D95694%7Chk%3D237f87af54e2d66080c158012842543058513dcb'
        ]
        detail_args = {
            'image_url': 'test data',
            'cate_id': 'test data',
            'rnk': 'test data',
            'nv_mid': 'test data',
            'item_url': 'test data',
            'item_nm': 'test data',
        }
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_best_100_in_detail, cb_kwargs=detail_args)
        '''
        if category_test_link:
            cb_kwargs = {'cate_name': 'test', 'depth': 1, 'pre_categories': {}}

            urls = [
                category_test_link
            ]
            # yield scrapy.Request(url="http://httpbin.org/ip", callback=self.chk_ip)
            for url in urls:
                yield scrapy.Request(url=url, callback=self.parse_morethan_second_depth,
                                     cb_kwargs=cb_kwargs,
                                     # headers={'User-Agent': str(ua.chrome)}
                                     )

    def parse_first_depth(self, response):
        """
            1depth 카테고리 파싱
        """
        '''
            카테고리 파싱 첫번째 방법
        '''
        container = response.css('li._category_area_li a')
        for li in container:
            cate_name = li.css('a img::attr(alt)').get()
            link = li.css('a::attr(href)').get()
            logging.log(logging.INFO, 'depth: [{0}]'.format(1) + ',cate_name: ' + cate_name + ': ' + link)
            cb_kwargs = {'cate_name': cate_name, 'depth': 1, 'pre_categories': []}

            yield response.follow(link,
                                  callback=self.parse_morethan_second_depth,
                                  cb_kwargs=cb_kwargs,
                                  # headers={'User-Agent': str(ua.chrome)}
                                  )
        '''
            두번째 방법
        '''
        # yield from response.follow_all(links, callback=self.parse_second_depth)

        '''
            분석 페이지 생성
        '''
        # page = response.url.split("/")[-2]
        # filename = 'quotes-%s.html' % page
        # with open(filename, 'wb') as f:
        #     f.write(response.body)
        # self.log('Saved file %s' % filename)

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
                key = info.css('span::text').get().strip()
                if key == info_key:
                    res = info.css('em::text').get()
                    break

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
        try:
            item_details = {
                'seller_cnt': response.css('#snb > ul > li.mall_place.on > a > em::text').get(),
                'single_mall_nm': get_single_mall_name(top_mall_list),
                'rate': response.css('#container > div.summary_area > div.summary_info.'
                                     '_itemSection > div > div.h_area > div > div.gpa::text').get(),
                'prefer_age1': get_age_grades(chart, 1),
                'prefer_age2': get_age_grades(chart, 2),
                'female_rate': response.css('#modelDemographyGraph > div.chart_area > div.gender._gender::attr(data-f)').get(),
                'min_price': response.css('#content > div > div.summary_cet > div.price_area > span > em::text').get(),
                'manufacturer': get_goods_info(goods_info, '제조사'),
                'brand': get_goods_info(goods_info, '브랜드'),
                'reg_date': get_goods_info(goods_info, '등록일').replace(".", "-") + "01",
                'wish_cnt': response.css('#jjim > em.cnt._keepCount::text').get(),
                'review_cnt': response.css('#snb > ul > li.mall_review > a > em::text').get(),
                'storefarm_num': len(sf),
                'top_store_num': len(top_mall_list),
            }
            item_details.update(cb_kwargs)
            # 데이터 구분값
            item_details['type'] = 'nvshop_best_item'
        except Exception as e:
            print(cb_kwargs['item_nm'])
        try:
            logging.log(logging.INFO, '카테고리 :' + cb_kwargs['cate_name'] + '/ 이름: ' + item_details['item_nm'])
        except Exception as e:
            print('no cate_name')

        yield item_details
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
                'fixeddate': str(datetime.now()),
            }
            keyword_data.update(cb_kwargs)

            yield keyword_data

    def parse_best_brand(self, response, **cb_kwargs):
        rnk_list = response.css('#popular_srch_lst > li')

        for rnk in rnk_list:
            rnk_flg = rnk.css('span.vary span::text').get().strip()
            elev_width = int(rnk.css('span.vary::text')[1].get().strip() or 0)

            brand_data = {
                'rnk': rnk.css('em::text').get()[:-1],
                'keyword': rnk.css('span.txt a::attr(title)').get().strip(),
                'trend': elev_width if rnk_flg == '상승' else elev_width * -1 if rnk_flg == '하락' else 0,
                'fixeddate': str(datetime.now()),
            }
            brand_data.update(cb_kwargs)

            yield brand_data



    def parse_morethan_second_depth(self, response, **cb_kwargs):
        """
            2depth 이상 카테고리 파싱
        """
        # print(cb_kwargs)
        # print('requests headers: ', response.request.headers)
        depth = cb_kwargs['depth'] + 1
        pre_categories = cb_kwargs['pre_categories']
        cate_id = parse_qs(urlparse(response.request.url).query)['catId'][0]
        current_categories = sorted(
            list(
                filter(lambda x: x != '', map(lambda x: x.strip(),
                                              response.css('div[id=srh_category1] ul li a em::text').getall() or [])
                       )
            )
        )
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
                    'rnk': idx,# item.css('.thumb_area div.best_rnk em::text').get(),
                    'nv_mid': item.attrib['data-nv-mid'],
                    'item_url': item.css('.thumb_area a::attr(href)').get(),
                    'item_nm': item.css('p > a::attr(title)').get(),
                    'cate_name': cb_kwargs['cate_name'],
                    'depth': cb_kwargs['depth']
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
                        'type': 'nvshop_best_item'
                    }
                    details.update(detail_args)
                    logging.log(logging.INFO, '카테고리 :' + details['cate_name'] + '/ 이름: ' + details['item_nm'])
                    yield details
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

        if depth >= category_depth_setting:
            return

        """
            카테고리 체인 파싱 max 4depth 
            ** recursive
        """
        if pre_categories != current_categories:
            container = response.css('div[id=srh_category1] ul li a')
            for a in container:
                cate_name = a.css('em::text').get().strip()
                link = a.attrib['href']
                logging.log(logging.INFO, 'depth: [{0}]'.format(depth) + ',cate_name: ' + cate_name + ': ' + link)
                cb_kwargs = {'cate_name': cate_name, 'depth': depth, 'pre_categories': current_categories}

                yield response.follow(link,
                                      callback=self.parse_morethan_second_depth,
                                      cb_kwargs=cb_kwargs,
                                      # headers={'User-Agent': str(ua.chrome)}
                                      )
