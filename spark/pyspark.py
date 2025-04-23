# from pyspark.sql import SparkSession

# JOB_NAME: str = ""

# spark = SparkSession.builder \
#     .master("spark://localhost[*]") \
#     .appName(JOB_NAME) \
#     .getOrCreate()


# from pyspark.sql import SparkSession

# spark = SparkSession.builder.appName("demo").getOrCreate()

# df = spark.createDataFrame(
#     [
#         ("sue", 32),
#         ("li", 3),
#         ("bob", 75),
#         ("heo", 13),
#     ],
#     ["first_name", "age"],
# )

# df.show()


# pyspark_emr.py
from pyspark.sql import SparkSession
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    spark = SparkSession.builder \
        .appName("EMR-Safe-Job") \
        .config("spark.submit.deployMode", "cluster") \
        .getOrCreate()

    try:
        df = spark.read.parquet(args.input)
        print(f"Read {df.count()} rows from {args.input}")
        df.write.mode("overwrite").parquet(args.output)
        print(f"Wrote output to {args.output}")
    except Exception as e:
        print(f"FAILED: {str(e)}")
        raise
    finally:
        spark.stop()

if __name__ == "__main__":
    main()