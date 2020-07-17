from math import ceil, floor
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse, urlsplit

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

