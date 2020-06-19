import pythena
import boto3

athena_client = pythena.Athena(database='tenbyten'
                               , region='ap-northeast-2'
                               , session=boto3.session.Session(aws_access_key_id="AKIAIZJ6FGUDMED7YKJA"
                                                               , aws_secret_access_key="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")
                               )
sql = 'select * from nvshop_best_brand where year = 2020 and month = 6 and day = 18 limit 10;'
df = athena_client.execute(sql)
# li = list(df)
print(df)
print(type(df[0].loc[0]['keyword']))
li = df[0]['keyword'].tolist()
print(type(list))
print(li)