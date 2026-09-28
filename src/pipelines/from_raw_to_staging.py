import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "core"))
sys.path.append(str(Path(__file__).parent.parent / "infrastructure" / "spark"))
sys.path.append(str(Path(__file__).parent.parent / "jobs" / "raw"))


from config import get_config
from session import get_spark_session
from extract_data_from_s3_raw import get_extract_data_from_s3_raw
from transform_data_from_s3_raw import get_transform_data_from_s3_raw
from load_transformed_data_from_s3_to_postgres_ods import get_load_transformed_data_from_s3_to_postgres_ods

def etl_from_s3_raw_to_postgres_staging():
    postgres_config = get_config('postgres_config')
    s3_config = get_config('s3_config')

    spark = get_spark_session()

    data_from_s3_raw = get_extract_data_from_s3_raw(spark, s3_config)

    transformed_data_from_s3_raw = get_transform_data_from_s3_raw(postgres_config, data_from_s3_raw)

    get_load_transformed_data_from_s3_to_postgres_ods(postgres_config, transformed_data_from_s3_raw)

    spark.stop()

if __name__ == "__main__":
    etl_from_s3_raw_to_postgres_staging()