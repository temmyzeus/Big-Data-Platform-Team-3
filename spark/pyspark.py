from pyspark.sql import SparkSession

JOB_NAME: str = ""

spark = SparkSession.builder \
    .master("...") \
    .appName(JOB_NAME) \
    .getOrCreate()

