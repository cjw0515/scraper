from math import ceil, floor

def get_page_data(target_arr, max_page, page):
    total_cnt = len(target_arr)
    max_page = max_page
    item_per_page = ceil(total_cnt / max_page)

    current_page = page
    total_pages = ceil(total_cnt / item_per_page)

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