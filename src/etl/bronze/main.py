from pyspark.sql.functions import (
    col, 
    count,
    current_timestamp,
    isnan,
    isnull,
    lit,
    when,
    row_number
)
from pyspark.sql.types import (
    StructType,
    StructField,
    IntegerType,
    StringType,
    DateType,
    TimestampType
)
from pyspark.sql import DataFrame
from pyspark.sql.window import Window

from ...config.spark_session import create_spark_session
from ...utils.reader import read_parquet

APP_NAME: str = "raw_data_processing"
RAW_USERS_DATA_S3_URI: str = "s3://big-data-platform-team-3/etl/oltp_data_dumps/users/*.parquet"
RAW_LISTINGS_DATA_S3_URI: str = "s3://big-data-platform-team-3/etl/oltp_data_dumps/listings/*.parquet"

def add_metadata_to_raw_df(df: DataFrame) -> DataFrame:
    return df.withColumn(
            "load_timestamp",
            current_timestamp()
        ).withColumn(
            "source_system",
            lit("Oracle Production Database")
        )

def validate_schema(df: DataFrame, schema: StructType, enforce: bool = False) -> DataFrame:
    if df.schema != schema:
        print("Schema Mismatch Detected!!!")

        if enforce:
            # return 
            return spark.createDataFrame(df.rdd, schema=schema)

    return df

def basic_data_quality_checks(df: DataFrame):
    """
    Logging (No Fiter) Basic Data Quality Checksz
    """
    total_rows: int = df.count()
    for c in df.columns:
        df.select(
            isnull(col(c)) 
        )

def analyze_data_quality(df, table_name):
    # Count nulls in each column
    null_counts = df.select([count(when(col(c).isNull() | isnan(c), c)).alias(c) for c in df.columns])
    
    # Calculate completeness percentage
    total_rows = df.count()
    completeness = {c: 100 * (1 - null_counts.first()[c] / total_rows) for c in df.columns}
    
    # Log data quality metrics
    for column, comp_pct in completeness.items():
        print(f"{table_name}.{column}: {comp_pct:.2f}% complete")
        
    return completeness


spark = create_spark_session(APP_NAME) \
        .getOrCreate()
raw_users_df = read_parquet(spark, [RAW_USERS_DATA_S3_URI])
raw_listings_df = read_parquet(spark, [RAW_LISTINGS_DATA_S3_URI])

# Schema Validation and Enforcement
expected_raw_user_schema = StructType([
    StructField("user_id", IntegerType(), False),
    StructField("user_type", StringType(), False),
    StructField("registration_date", DateType(), False),
    StructField("email_verified", StringType(), False),
    StructField("location", StringType(), True),
    StructField("last_login", TimestampType(), False)
])
expected_raw_listings_schema = StructType([
    StructField("listing_id", IntegerType(), False),
    StructField("vehicle_id", StringType(), False),
    StructField("seller_id", StringType(), False),
    StructField("make", StringType(), False),
    StructField("model", StringType(), False),
    StructField("year", IntegerType(), False),
    StructField("price", IntegerType(), False),
    StructField("category", StringType(), False),
    StructField("is_used", StringType(), False),
    StructField("listing_date", DateType(), False),
    StructField("status", StringType(), False),
    StructField("location", StringType(), True),
    StructField("mileage", IntegerType(), True),
    StructField("condition", StringType(), True),
    StructField("is_featured", StringType(), True),
    StructField("seller_type", StringType(), True)
])

# Validate Schema
users_df = validate_schema(raw_users_df, expected_raw_user_schema)
listings_df = validate_schema(raw_listings_df, expected_raw_listings_schema)

# Metadata Enrichment
users_df = add_metadata_to_raw_df(raw_users_df)
users_df = add_metadata_to_raw_df(raw_listings_df)

# Basic Data Quality Checks

user_data_quality = analyze_data_quality(users_df, "users")
listing_data_quality = analyze_data_quality(listings_df, "listings")

# Handle Duplicated, partitioning and optimization
# Identify potential duplicates in users table
user_duplicates = users_df.groupBy("user_id").count().filter("count > 1")

# For bronze layer, we typically preserve duplicates but flag them
if user_duplicates.count() > 0:
    print(f"Warning: {user_duplicates.count()} duplicate user records found")
    
    # Add duplicate flag
    windowed_users = Window.partitionBy("user_id").orderBy("load_timestamp")
    users_df = users_df.withColumn("duplicate_flag", 
                                   when(row_number().over(windowed_users) > 1, True)
                                   .otherwise(False))


users_df.write \
    .mode("append") \
    .parquet("s3://big-data-platform-team-3/etl/bronze/listings_data/")

listings_df.write \
    .mode("append") \
    .parquet("s3://big-data-platform-team-3/etl/bronze/users_data/")

spark.stop()
