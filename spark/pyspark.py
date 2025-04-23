# from pyspark.sql import SparkSession

# JOB_NAME: str = ""

# spark = SparkSession.builder \
#     .master("spark://localhost[*]") \
#     .appName(JOB_NAME) \
#     .getOrCreate()


from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("demo").getOrCreate()

df = spark.createDataFrame(
    [
        ("sue", 32),
        ("li", 3),
        ("bob", 75),
        ("heo", 13),
    ],
    ["first_name", "age"],
)

df.show()