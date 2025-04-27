from pyspark.sql import SparkSession, DataFrame

def read_parquet(
        spark: SparkSession, 
        source_uris: list[str], 
        options: dict = {}
    ) -> DataFrame:
    
    # Set mergeSchema option if `mergeSchema` or `spark.sql.parquet.mergeSchema` is not explicitely set
    if (not options.get("mergeSchema")) or (not options.get("spark.sql.parquet.mergeSchema")):
        options["mergeSchema"] = True

    return (
            spark.read
            .parquet(
                *source_uris,
                **options
            )
        )
