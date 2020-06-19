import scrapy


class QuotesSpider(scrapy.Spider):
    # 스파이더의 식별자. 프로젝트 내에서 유일해야한다.
    name = "quotes"

    custom_settings = {
        'ITEM_PIPELINES': {
            'naver_scrap.pipelines.NaverScrapPipeline': 300,
        }
    }

    # 스파이더가 크롤링을 시작할 반복 요청 (요청 목록을 반환하거나 생성기 함수를 작성할 수 있음)을 반환해야합니다. 후속 요청은 이러한 초기 요청에서 연속적으로 생성됩니다.
    def start_requests(self):
        urls = [
            'http://quotes.toscrape.com/page/1/',
            'http://quotes.toscrape.com/page/2/',
        ]
        # 함수 안에서 yield를 사용하면 함수는 제너레이터가 되며 yield에는 값을 지정한다.
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    # 각 요청에 대해 다운로드 된 응답을 처리하기 위해 호출되는 메소드
    def parse(self, response):
        # response 매개 변수는 페이지 컨텐츠를 보유하고이를 처리하는 데 유용한 추가 메소드가있는 TextResponse의 인스턴스.
        for quote in response.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').get(),
                'author': quote.css('small.author::text').get(),
                'tags': quote.css('div.tags a.tag::text').getall(),
            }
    '''        
        page = response.url.split("/")[-2]
        filename = 'quotes-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
    '''
