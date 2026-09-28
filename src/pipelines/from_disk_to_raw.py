import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "core"))
sys.path.append(str(Path(__file__).parent.parent / "infrastructure" / "spark"))
sys.path.append(str(Path(__file__).parent.parent / "jobs" / "raw"))

from config import get_config
from session import get_spark_session
from extract_data_from_disk import get_extract_data_from_disk
from load_data_from_disk_to_minio_raw import get_load_data_from_disk_to_minio_raw

def el_from_disk_to_s3_raw():
    postgres_config = get_config('postgres_config')
    s3_config = get_config('s3_config')

    spark = get_spark_session()

    data_from_disk = get_extract_data_from_disk(spark, s3_config)

    get_load_data_from_disk_to_minio_raw(data_from_disk)

    spark.stop()

if __name__ == "__main__":
    el_from_disk_to_s3_raw()