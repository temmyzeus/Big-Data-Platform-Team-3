from botocore.client import Config
from botocore.session import get_session

session = get_session()
s3 = session.create_client('s3', config=Config(signature_version='s3v4'))

bucket_name = 'big-data-platform-team-3'
s3_key = 'car_sales_data.parquet'
local_file = 'data/car_sales_data.parquet'


def upload_parquet_file(local_file, bucket_name, s3_key) -> None:
    try:
        with open(local_file, 'rb') as f:
            s3.put_object(Bucket=bucket_name, Key=s3_key, Body=f)
        print(f"File uploaded to s3://{bucket_name}/{s3_key}")
    except Exception as e:
        print("Upload failed:", e)
