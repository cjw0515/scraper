# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from fake_useragent import UserAgent
from urllib.parse import urlparse, parse_qs

ua = UserAgent()
'''
    depth 제한 
    최대 4 최소 2
'''
category_depth_setting = 1
log_level = 'ERROR'


class NaverBest100CategorySpider(scrapy.Spider):
    name = 'naver_best100_category'
    custom_settings = {
        # 'AUTOTHROTTLE_ENABLED': True,
        # 'AUTOTHROTTLE_START_DELAY': 5,
        # 'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0,
        'DOWNLOAD_DELAY': 0.5,
        'LOG_LEVEL': log_level,
        'ITEM_PIPELINES': {
            'naver_scrap.pipelines.NaverScrapPipeline': 300,
        }
    }

    def __init__(self, category=None, *args, **kwargs):
        super(NaverBest100CategorySpider, self).__init__(*args, **kwargs)
        self.category_depth_setting = category_depth_setting

    def start_requests(self):
        urls = [
            'https://search.shopping.naver.com/best100v2/main.nhn'
        ]
        # yield scrapy.Request(url="http://httpbin.org/ip", callback=self.chk_ip)
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_first_depth)

        # urls = [
        #     'https://search.shopping.naver.com/detail/detail.nhn?cat_id=50002170&nv_mid=20811239770&NaPm=ct%3Dkb0e7u80%7Cci%3D1999b2bad27c658327cfac0541fcc1e1ab185c7d%7Ctr%3Dsl%7Csn%3D95694%7Chk%3D237f87af54e2d66080c158012842543058513dcb'
        # ]
        # detail_args = {
        #     'image_url': 'test data',
        #     'cate_id': 'test data',
        #     'rnk': 'test data',
        #     'nv_mid': 'test data',
        #     'item_url': 'test data',
        #     'item_nm': 'test data',
        # }
        # for url in urls:
        #     yield scrapy.Request(url=url, callback=self.parse_best_100_in_detail, cb_kwargs=detail_args)


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
            print('depth: ', '[{0}]'.format(1), ',', 'cate_name: ', cate_name, ': ', link)
            cb_kwargs = {'cate_name': cate_name, 'depth': 1, 'pre_categories': []}
            yield response.follow(link,
                                  callback=self.parse_morethan_second_depth,
                                  cb_kwargs=cb_kwargs,
                                  headers={'User-Agent': str(ua.chrome)})
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

        def get_storefarm_ratio(top_mall_list, sf):
            return str(len(sf)) + '/' + str(len(top_mall_list)) if len(sf) != 0 else 0

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
                'reg_date': get_goods_info(goods_info, '등록일'),
                'wish_cnt': response.css('#jjim > em.cnt._keepCount::text').get(),
                'review_cnt': response.css('#snb > ul > li.mall_review > a > em::text').get(),
                'storefarm_ratio': get_storefarm_ratio(top_mall_list, sf)
            }
            item_details.update(cb_kwargs)
            # print(item_details)
        except Exception as e:
            print(cb_kwargs['item_nm'])
        try:
            print('카테고리 :', cb_kwargs['cate_name'], '/ 이름: ', item_details['item_nm'])
        except Exception as e:
            print('no cate_name')

        yield item_details



    def chk_ip(self, response):
        print(response.text)

    def parse_morethan_second_depth(self, response, **cb_kwargs):
        """
            2depth 이상 카테고리 파싱
        """
        # print(cb_kwargs)
        # print('requests headers: ', response.request.headers)
        depth = cb_kwargs['depth'] + 1
        pre_categories = cb_kwargs['pre_categories']
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
            best100 파싱            
        """
        best_100 = response.css('div[id=productListArea] ul li')
        cate_id = parse_qs(urlparse(response.request.url).query)['catId'][0]
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
            # if idx == 23:
            #     print(detail_args)
            yield response.follow(detail_args['item_url'],
                                  callback=self.parse_best_100_in_detail,
                                  cb_kwargs=detail_args,
                                  headers={'User-Agent': str(ua.chrome)})


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
                print('depth: ', '[{0}]'.format(depth), ',', 'cate_name: ', cate_name, ': ', link)
                cb_kwargs = {'cate_name': cate_name, 'depth': depth, 'pre_categories': current_categories}

                yield response.follow(link,
                                      callback=self.parse_morethan_second_depth,
                                      cb_kwargs=cb_kwargs,
                                      headers={'User-Agent': str(ua.chrome)})
