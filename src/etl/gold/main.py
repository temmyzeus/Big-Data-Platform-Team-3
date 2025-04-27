from pyspark.sql.functions import col, current_timestamp, lit, datediff, current_date, concat_ws, when

from ...config.spark_session import create_spark_session
from ...utils.reader import read_parquet

def create_user_dimension(silver_users_df):
    # Start with current silver users (filter for current records only)
    user_dim_df = silver_users_df.filter(col("is_current") == True)
    
    # Select and rename relevant columns for the dimension table
    user_dim_df = user_dim_df.select(
        col("surrogate_key").alias("user_key"),
        col("user_id").alias("user_id"),
        col("full_name").alias("user_name"),
        col("email").alias("user_email"),
        col("user_status").alias("status"),
        col("created_at_utc").alias("created_date"),
        col("account_age_days").alias("tenure_days"),
        # Additional attributes needed for user analysis
        col("last_login_date"),
        col("city").alias("user_city"),
        col("state").alias("user_state"),
        col("country").alias("user_country")
    )
    
    # Add user segmentation (a gold layer enrichment)
    user_dim_df = user_dim_df.withColumn(
        "user_segment",
        when(col("tenure_days") < 30, "new")
        .when(col("tenure_days") >= 30 & col("tenure_days") < 180, "growing")
        .when(col("tenure_days") >= 180 & col("tenure_days") < 365, "established")
        .otherwise("veteran")
    )
    
    # Add recency dimension
    user_dim_df = user_dim_df.withColumn(
        "days_since_last_login", 
        datediff(current_date(), col("last_login_date"))
    )
    
    user_dim_df = user_dim_df.withColumn(
        "recency_segment",
        when(col("days_since_last_login").isNull(), "never_logged_in")
        .when(col("days_since_last_login") <= 7, "active_recent")
        .when(col("days_since_last_login") <= 30, "active_month")
        .when(col("days_since_last_login") <= 90, "inactive_quarter")
        .otherwise("dormant")
    )
    
    # Add metadata
    user_dim_df = user_dim_df.withColumn("etl_updated_at", current_timestamp())
    
    return user_dim_df

# Create the user dimension table

APP_NAME = "AutoMarketplace Gold"
spark = create_spark_session(APP_NAME)
users_df = read_parquet(spark)
listings_df = read_parquet(spark)

# Apply the transformation
user_dim_df = create_user_dimension(users_df)

def create_listing_dimension(silver_listings_df):
    # Select and rename relevant columns
    listing_dim_df = silver_listings_df.select(
        col("listing_id").alias("listing_key"),
        col("listing_title").alias("listing_name"),
        col("price").alias("listing_price"),
        col("price_category").alias("price_tier"),
        col("listing_date").alias("created_date"),
        col("listing_status").alias("status"),
        col("is_active").alias("is_active"),
        col("listing_age_days").alias("days_on_market"),
        col("category").alias("listing_category"),
        col("city").alias("listing_city"),
        col("state").alias("listing_state"),
        col("zip_code").alias("listing_postal_code"),
        col("user_id").alias("seller_id")
    )
    
    # Add listing segmentation
    listing_dim_df = listing_dim_df.withColumn(
        "listing_age_segment",
        when(col("days_on_market") <= 7, "new")
        .when(col("days_on_market") <= 30, "recent")
        .when(col("days_on_market") <= 90, "standard")
        .otherwise("stale")
    )
    
    # Add geographical hierarchy for drill-down analytics
    listing_dim_df = listing_dim_df.withColumn(
        "geo_key", 
        concat_ws("_", col("listing_city"), col("listing_state"), col("listing_postal_code"))
    )
    
    # Add metadata
    listing_dim_df = listing_dim_df.withColumn("etl_updated_at", current_timestamp())
    
    return listing_dim_df

# Create the listing dimension table
listing_dim_df = create_listing_dimension(listings_df)
