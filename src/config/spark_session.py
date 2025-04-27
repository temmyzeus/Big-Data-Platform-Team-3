from pyspark.sql import SparkSession

def create_spark_session(app_name: str) -> SparkSession.Builder:
    """
    Get SparkSession .builder() object, on which .getOrCreate() can be \
    used to get the Spark Session. Its written this way, so go the builder can have its configurations extended.
    """
    return (
        SparkSession.builder
        .master("yarn")
        .appName(app_name)
        .config("spark.submit.deployMode", "Cluster")
    )
