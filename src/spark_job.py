from pyspark.sql import SparkSession, DataFrame
import pyspark.sql.functions as F
import argparse

USERS_DATA_S3_URI: str = "s3://big-data-platform-team-3/etl/bronze/users_data/*.parquet"
LISTINGS_DATA_S3_URI: str = "s3://big-data-platform-team-3/bronze/etl/listings_data/*.parquet"

def load_parquet_data(spark: SparkSession, url: str, load_options: dict = {}) -> DataFrame:
    return (
        spark
        .read
        .options(**load_options)
        .parquet(url)
    )

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

        users_df: DataFrame = load_parquet_data(
                spark, 
                USERS_DATA_S3_URI, 
                {"mergeSchema": True}
            )
        
        listing_df: DataFrame = load_parquet_data(
                spark, 
                LISTINGS_DATA_S3_URI, 
                {"mergeSchema": True}
            )
        
        users_df.printSchema()
        listing_df.printSchema()

        # Clean 
        # listing_df.join(
        #     users_df,
        #     on=users_df.user_id == listing_df.seller_id,
        #     how="left"
        # )

    except Exception as e:
        print(f"FAILED: {str(e)}")
        raise
    finally:
        spark.stop()

if __name__ == "__main__":
    main()