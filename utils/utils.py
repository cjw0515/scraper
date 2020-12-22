from math import ceil, floor
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse, urlsplit
import requests
from scrapy.http import HtmlResponse
from scrapy.selector import Selector
import json

def get_page_data(target_arr, max_page, page):
    total_cnt = len(target_arr)
    max_page = max_page
    item_per_page = floor(total_cnt / max_page)

    current_page = page
    total_pages = max_page

    # print('total_cnt: ', total_cnt)
    # print('max_page: ', max_page)
    # print('total_pages: ', total_cnt / item_per_page)

    st_num = (
                 (current_page - 1) * item_per_page + 1
                 if current_page <= total_pages
                 else (total_pages - 1) * item_per_page
             ) - 1
    end_num = (
                  item_per_page * current_page
                  if current_page < total_pages
                  else total_cnt
              )


    return target_arr[st_num:end_num]

def qs_replace(org_url, key_to_change, val_to_change):
    parts = urlparse(org_url)
    qs = dict(parse_qsl(parts.query))

    qs[key_to_change] = val_to_change
    parts = parts._replace(query=urlencode(qs))
    new_url = urlunparse(parts)

    return new_url

def get_qs(url):
    parts = urlparse(url)
    return dict(parse_qsl(parts.query))

def rec_request(url, params=None, headers=None, retry=10):
    res = requests.get(url, params=params, headers=headers)
    if res.status_code == 200 or retry <= 0:
        return res
    else:
        return rec_request(url, params=params, headers=headers, retry=retry-1)


if __name__ == "__main__":
    url = "https://search.shopping.naver.com/catalog/24407717556?cat_id=50000831&nv_mid=24407717556&NaPm=ct%3Dkizeljnk%7Cci%3Dbdcbdcc2e0399d25d8afcdc93af890de1c16e0b6%7Ctr%3Dsl%7Csn%3D95694%7Chk%3D8ed4c0e787209d6f915ce4d354273bfecb31d0fc"
    response = rec_request(url=url)
    res = HtmlResponse(url=url, body=response.content)
    res = Selector(response=res)
    dataLab = json.loads(res.css("#__NEXT_DATA__::text").get())['props']['pageProps']['initialState']['catalog']['dataLab']
    info = json.loads(res.css("#__NEXT_DATA__::text").get())['props']['pageProps']['initialState']['catalog']['info']
    rc = info['reviewCount']
    pc = info['productCount']
    fv = [x for x in dataLab['genderDemoValues'] if x['gender'] == 'F'][0]['value']
    pa1 = [x for x in dataLab['ageDemoValues'] if x['rank'] == '1'][0]['age']
    pa2 = [x for x in dataLab['ageDemoValues'] if x['rank'] == '2'][0]['age']
    print(dataLab)
    print(fv)
    print(pa1)
    print(pa2)
    print(rc)
    print(pc)
