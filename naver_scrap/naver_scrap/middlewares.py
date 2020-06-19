# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message
from time import sleep
import logging
from scrapy.http import HtmlResponse
from scrapy.utils.python import to_bytes

from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class NaverScrapSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class NaverScrapDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class SleepRetryMiddleware(RetryMiddleware):
    def __init__(self, settings):
        RetryMiddleware.__init__(self, settings)

    def process_response(self, request, response, spider):
        if response.status in [429]:
            logging.log(logging.ERROR, 'sleep 30 seconds... at ' + request.url)
            sleep(30)
            reason = response_status_message(response.status)
            return self._retry(request, reason, spider) or response

        return super(SleepRetryMiddleware, self).process_response(request, response, spider)


class SeleniumMiddleware(object):
    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def spider_opened(self, spider):
        CHROMEDRIVER_PATH = 'C:/scraper/naver_scrap/naver_scrap/drivers/chromedriver.exe'  # Windows는 chromedriver.exe로 변경
        WINDOW_SIZE = "1920,1080"

        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument(f"--window-size={WINDOW_SIZE}")
        prefs = {'download.default_directory': 'C:\Test'}
        chrome_options.add_experimental_option('prefs', prefs)

        driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=chrome_options)
        self.driver = driver

    def spider_closed(self, spider):
        self.driver.close()

    def process_request(self, request, spider):
        self.driver.get(request.url)
        el_input = self.driver.find_element_by_xpath('//*[@id="item_sub_keyword1_1"]')
        el_period_btn = self.driver.find_element_by_xpath('//*[@id="content"]/div/div[2]/div[1]/div/form/fieldset/div/div[6]/div[1]/label[3]')
        el_submit_btn = self.driver.find_element_by_xpath('//*[@id="content"]/div/div[2]/div[1]/div/form/fieldset/a')

        el_input.send_keys("사과")
        el_period_btn.click()
        el_submit_btn.click()

        body = ''
        try:
            if self.driver.current_url == request.url:
                WebDriverWait(self.driver, 5).until(
                    # EC.presence_of_element_located((By.ID, "graph_data"))
                    EC.url_changes(self.driver.current_url)
                )
                for req in self.driver.requests:
                    print(
                        'path: ', req.path,
                        'code: ', req.response.status_code,
                        'content-type: ', req.response.headers['Content-Type']
                    )
                    if req.response and req.path == 'https://datalab.naver.com/keyword/trendResult.naver?hashKey=N_31c43b58aa7037ab4e2392a581867442':
                        print(req.response.body)
                        body = req.response.body

                        # body = to_bytes(text=self.driver.page_source)
        finally:
            self.driver.quit()
            return HtmlResponse(url=request.url, body=body, encoding='utf-8', request=request)


class NaverScrapDownloaderProxyMiddleware(object):
    def process_request(self, request, spider):
        request.meta['proxy'] = "http://127.0.0.1:8118"