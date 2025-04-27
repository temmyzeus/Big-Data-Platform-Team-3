from pyspark.sql.functions import (
    col, 
    lower, 
    trim, 
    regexp_replace, 
    when, 
    lit,
    datediff, 
    current_date, 
    year, 
    month, 
    dayofmonth, 
    concat_ws,
    row_number, 
    monotonically_increasing_id,
    current_timestamp
)
from pyspark.sql.window import Window

from ...config.spark_session import create_spark_session
from ...utils.reader import read_parquet

def clean_users_table(bronze_users_df):

    silver_users_df = bronze_users_df.withColumn(
        "email", 
        lower(trim(col("email")))
    )
    
    silver_users_df = silver_users_df.withColumn(
        "phone_number", 
        regexp_replace(col("phone_number"), "[^0-9+-]", "")
    )
    
    silver_users_df = silver_users_df.withColumn(
        "first_name", 
        when(col("first_name").isNull() | (trim(col("first_name")) == ""), 
             lit("Unknown")).otherwise(trim(col("first_name")))
    )
    
    # ToDo: Convert timestamps to standardized timezone (UTC)
    
    return silver_users_df


def enrich_users_schema(silver_users_df):
    # Calculate account age in days
    silver_users_df = silver_users_df.withColumn(
        "account_age_days", 
        datediff(current_date(), col("registration_date"))
    )
    
    # Extract date parts for time intelligence
    silver_users_df = silver_users_df \
        .withColumn("created_year", year(col("registration_date"))) \
        .withColumn("created_month", month(col("registration_date"))) \
        .withColumn("created_day", dayofmonth(col("registration_date")))
    
    # Create a full_name field
    silver_users_df = silver_users_df.withColumn(
        "full_name", 
        concat_ws(" ", col("first_name"), col("last_name"))
    )
    
    # Add user status based on activity (example rule)
    silver_users_df = silver_users_df.withColumn(
        "user_status",
        when(col("account_age_days") < 30, "new")
        .when(col("last_login_date").isNull() | 
              datediff(current_date(), col("last_login_date")) > 90, "inactive")
        .otherwise("active")
    )
    
    return silver_users_df


APP_NAME: str = "Bronze_Marketplace"

spark = create_spark_session(APP_NAME)
bronze_users_df = read_parquet(spark)

# Apply the transformation
silver_users_df = clean_users_table(bronze_users_df)

# Apply the enrichment
silver_users_df = enrich_users_schema(silver_users_df)


def implement_user_scd(bronze_users_df, existing_silver_users_df):
    # Assign a unique sequence ID to each version of a user record
    window_spec = Window.partitionBy("user_id").orderBy("load_timestamp")
    
    # Process incoming bronze records
    new_silver_records = bronze_users_df \
        .withColumn("row_num", row_number().over(window_spec)) \
        .withColumn("is_current", lit(True)) \
        .withColumn("valid_from", col("load_timestamp")) \
        .withColumn("valid_to", lit(None).cast("timestamp")) \
        .withColumn("surrogate_key", monotonically_increasing_id())
    
    # Identify updated records by comparing with existing silver records
    if existing_silver_users_df is not None:
        # Find records that already exist in silver but have changed
        joined_df = new_silver_records \
            .join(
                existing_silver_users_df.filter(col("is_current") == True)
                .select("user_id", "email", "first_name", "last_name", "phone_number", "surrogate_key"),
                on="user_id", 
                how="left"
            )
        
        # Identify changed records
        changed_records = joined_df.filter(
            (col("email") != col("existing_silver_users_df.email")) | 
            (col("first_name") != col("existing_silver_users_df.first_name")) |
            (col("last_name") != col("existing_silver_users_df.last_name")) |
            (col("phone_number") != col("existing_silver_users_df.phone_number"))
        ).select("user_id", "surrogate_key")
        
        # Update existing records (mark old versions as not current)
        existing_silver_users_df = existing_silver_users_df \
            .join(changed_records, on="user_id", how="left") \
            .withColumn(
                "is_current", 
                when(col("changed_records.user_id").isNotNull(), False).otherwise(col("is_current"))
            ) \
            .withColumn(
                "valid_to", 
                when(col("changed_records.user_id").isNotNull(), current_timestamp()).otherwise(col("valid_to"))
            )
        
        # Combine existing and new records
        silver_users_df = existing_silver_users_df.union(new_silver_records)
    else:
        silver_users_df = new_silver_records
    
    return silver_users_df

# Apply SCD implementation
silver_users_df = implement_user_scd(bronze_users_df, silver_users_df)


# Writing the data to silver storage# Write Users table to silver layer
silver_users_df.write \
    .mode("overwrite") \
    .partitionBy("created_year", "created_month") \
    .parquet("silver.users")
