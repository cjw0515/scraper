import json
import requests
from global_settings import BOT_NAME

DAY_JOB_SEQUENCE = ['naver_best_category', 'naver_category', 'daangn_popular_goods', '1300k_best_item']
PROJECT_MAPPER = {
    'lightweight_scrap' : ['daangn_kwd_rank', 'daangn_popular_goods', '1300k_best_item'],
    'naver_scrap': ['naver_best_category', 'naver_category', 'naver_datalab_trend']
}
REQ_DATA_PER_BOT = {
    'bot1': {
        'naver_best_category': {
            'categories': "50000000,50000002",
        },
        'naver_datalab_trend': {
            'page': "1",
        },
        'naver_category': {
            'page': "1",
        },
        'daangn_popular_goods': {
            'page': "1",
        },
        '1300k_best_item': {
            'page': "1",
        },
    },
    'bot2': {
        'naver_best_category': {
            'categories': "50000003",
        },
        'naver_datalab_trend': {
            'page': "2",
        },
        'naver_category': {
            'page': "2",
        },
        'daangn_popular_goods': {
            'page': "2",
        },
        '1300k_best_item': {
            'page': "2",
        },
    },
    'bot3': {
        'naver_best_category': {
            'categories': "50000004,50000006",
        },
        'naver_datalab_trend': {
            'page': "3",
        },
        'naver_category': {
            'page': "3",
        },
        'daangn_popular_goods': {
            'page': "3",
        },
        '1300k_best_item': {
            'page': "3",
        },
    },
    'bot4': {
        'naver_best_category': {
            'categories': "50000007,50000005",
        },
        'naver_datalab_trend': {
            'page': "4",
        },
        'naver_category': {
            'page': "4",
        },
        'daangn_popular_goods': {
            'page': "4",
        },
        '1300k_best_item': {
            'page': "4",
        },
    },
    'bot5': {
        'naver_best_category': {
            'categories': "50000001,50000008",
        },
        'naver_datalab_trend': {
            'page': "5",
        },
        'naver_category': {
            'page': "5",
        },
        'daangn_popular_goods': {
            'page': "5",
        },
        '1300k_best_item': {
            'page': "5",
        },
    },
    'local-pc': {
        'naver_best_category': {
            'categories': "50000001,50000008",
        },
        'naver_datalab_trend': {
            'page': "5",
        },
        'naver_category': {
            'categories': "50000008",
        },
        'daangn_popular_goods': {
            'page': "5",
        },
        '1300k_best_item': {
            'page': "5",
        },
    },
}

def get_project_name(spider_name):
    res = ""
    for key, value in PROJECT_MAPPER.items():
        if spider_name in value:
            res = key
            break

    return res

def get_next_job(spider_name):
    try:
        return DAY_JOB_SEQUENCE[DAY_JOB_SEQUENCE.index(spider_name) + 1]
    except Exception as e:
        return ''

def exec_next_job(spider_name):
    next_spider = get_next_job(spider_name)
    url = 'http://localhost:6800/schedule.json'
    data = {
        "project": get_project_name(next_spider),
        "spider": next_spider,
    }
    try:
        data.update(REQ_DATA_PER_BOT[BOT_NAME][next_spider])
        if next_spider:
            requests.post(url, data=data)
    except Exception as e:
        pass