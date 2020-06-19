import scrapy
import os
from platform import system
from scrapy.selector import Selector
from scrapy.utils.project import get_project_settings

from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent

from ast import literal_eval
import re

ua = UserAgent()
url_pattern = r'^(https:\/\/www\.|https:\/\/)(datalab.naver.com\/keyword\/trendResult.naver\?hashKey=)'
p = re.compile(url_pattern)

class NaverDataLabSpider(scrapy.Spider):
    # 스파이더의 식별자. 프로젝트 내에서 유일해야한다.
    name = "naver_datalab_trend"

    custom_settings = {
        'ITEM_PIPELINES': {
            'naver_scrap.pipelines.NaverScrapPipeline': 300,
        },
        'SPIDER_MIDDLEWARES': {
            'naver_scrap.middlewares.NaverScrapSpiderMiddleware': 543,
        },
        'DOWNLOADER_MIDDLEWARES': {
            'naver_scrap.middlewares.NaverScrapDownloaderMiddleware': 543,
            # 'naver_scrap.middlewares.SeleniumMiddleware': 100
        }
    }

    def __init__(self, *args, **kwargs):
        super(NaverDataLabSpider, self).__init__(*args, **kwargs)
        CHROMEDRIVER_PATH = os.path.join(get_project_settings().get('PROJECT_ROOT_PATH')
                                         , r"drivers/chromedriver{}".format(".exe" if system() == "Windows" else ""))
        # CHROMEDRIVER_PATH = 'C:/scraper/naver_scrap/naver_scrap/drivers/chromedriver.exe'  # Windows는 chromedriver.exe로 변경
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
    # 스파이더가 크롤링을 시작할 반복 요청 (요청 목록을 반환하거나 생성기 함수를 작성할 수 있음)을 반환해야합니다. 후속 요청은 이러한 초기 요청에서 연속적으로 생성됩니다.

    def start_requests(self):
        urls = ['https://datalab.naver.com/keyword/trendSearch.naver']

        # 함수 안에서 yield를 사용하면 함수는 제너레이터가 되며 yield에는 값을 지정한다.
        for url in urls:
            yield scrapy.Request(url=url,
                                 callback=self.start_req,
                                 headers={'User-Agent': str(ua.chrome)}
            )

    # 각 요청에 대해 다운로드 된 응답을 처리하기 위해 호출되는 메소드
    def start_req(self, response):
        def extract(driver):
            body = ''
            try:
                WebDriverWait(driver, 5).until(
                    # EC.presence_of_element_located((By.ID, "graph_data"))
                    EC.url_changes(driver.current_url)
                )
                for req in driver.requests:
                    # print(
                    #     'path: ', req.path,
                    #     'code: ', req.response.status_code,
                    #     'content-type: ', req.response.headers['Content-Type']
                    # )
                    if req.response and p.match(req.path) is not None:
                        body = req.response.body

                        # body = to_bytes(text=self.driver.page_source)
                selector = Selector(text=body)
                gragh_data = selector.css('#graph_data::text').get()
                res_data = literal_eval(gragh_data)
                return res_data[0]
            except Exception as e:
                print(e)

        def set_keyword(driver, keyword):
            el_input1 = driver.find_element_by_xpath('//*[@id="item_keyword1"]')
            el_input2 = driver.find_element_by_xpath('//*[@id="item_sub_keyword1_1"]')
            '#content > div > div.keyword_trend > div.section_step > div.com_box_inner > form > fieldset > div > div:nth-child(12) > div:nth-child(2) > button'
            el_period_btn = driver.find_element_by_css_selector(
                '#content > div > div.keyword_trend div.set_period > label[for=set_period3]')
            el_submit_btn = driver.find_element_by_css_selector(
                '#content > div > div.keyword_trend > div.section_step > div.com_box_inner > form > fieldset > a')
            el_input1.clear()
            el_input2.clear()
            el_input2.send_keys(keyword)
            el_period_btn.click()
            el_submit_btn.click()

        self.driver.get(response.request.url)

        keyword = ["사과", "과자"]

        for kwd in keyword:
            set_keyword(self.driver, kwd)
            res = extract(self.driver)
            for d in res['data']:
                dt = d['period']
                yield {
                    'keyword': kwd,
                    'period': '{}-{}-{}'.format(dt[:4], dt[4:6], dt[6:8]),
                    'value': d['value'],
                    'type': 'dlabtrend'
                }

        self.driver.quit()


