# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from fake_useragent import UserAgent

ua = UserAgent()
category_depth_setting = 8


class NaverBest100CategorySpider(scrapy.Spider):
    name = 'naver_best100_category'

    custom_settings = {}

    def start_requests(self):
        urls = [
            'https://search.shopping.naver.com/best100v2/main.nhn'
        ]
        # yield scrapy.Request(url="http://httpbin.org/ip", callback=self.chk_ip)
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse_first_depth)

    def parse_first_depth(self, response):
        container = response.css('li._category_area_li a')
        # links = response.css('li._category_area_li a::attr(href)').getall()

        '''
            첫번째 방법
        '''
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

    def chk_ip(self, response):
        print(response.text)

    def parse_morethan_second_depth(self, response, **cb_kwargs):
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
        if depth >= category_depth_setting:
            return

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
