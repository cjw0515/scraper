import pythena
import boto3
from math import ceil, floor
import os

athena_client = pythena.Athena(database='tenbyten'
                               , region='ap-northeast-2'
                               , session=boto3.session.Session(aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID']
                                                               , aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])

                         )

time_at = '20200625'
y = time_at[:4]
m = time_at[4:6]
d = time_at[6:8]

# sql = """
# select a.keyword
#      , row_number() over
# (order by a.keyword asc) as row
# from (
#   select distinct keyword
#     from nvshop_best_brand
#    where year = {}
#      and month = {}
#      and day = {}
#      and period = 'weekly'
# ) as a
# """.format(y, m, d)

sql = """
 select distinct keyword
    from nvshop_best_brand
   where year = {}
     and month = {}
     and day = {}
     and period = 'weekly'
   order by keyword
""".format(y, m, d)

df = athena_client.execute(sql)
kwds = df[0]['keyword'].tolist()

total_cnt = len(kwds)
max_page = 5
item_per_page = ceil(total_cnt / max_page)

current_page = 1
total_pages = ceil(total_cnt / item_per_page)

st_num = ((current_page - 1) * item_per_page + 1 if current_page <= total_pages else (total_pages - 1) * item_per_page) - 1
end_num = (item_per_page * current_page if current_page < total_pages else total_cnt) - 1


print('item_per_page: ', item_per_page)
print('st_num: ', st_num)
print('end_num: ', end_num)

res_arr = kwds[st_num:end_num]
print(kwds[0])
print(res_arr)
print(len(res_arr))



# 1 ~ 1960
# 1961 ~ 3920
# 3921 ~ 5880
# 5881 ~ 7840
# 7841 ~ 9798