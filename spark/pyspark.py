from pyspark.sql import SparkSession

JOB_NAME: str = ""

spark = SparkSession.builder \
    .master("spark://localhost[*]") \
    .appName(JOB_NAME) \
    .getOrCreate()

