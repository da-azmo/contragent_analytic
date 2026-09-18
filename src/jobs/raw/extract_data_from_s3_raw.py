from pyspark.sql import SparkSession
import sys
from pathlib import Path

sys_path = Path(__file__).parent.parent.parent / 'core'
sys.path.append(str(sys_path))

from metadata import get_s3_all_tables

def get_extract_data_from_s3_raw(spark: SparkSession, config: dict):
    data_from_s3_raw = {}

    tables = get_s3_all_tables(config, 'raw')

    for table in tables:
        target = table.get('target')

        try:
            df = spark.read.parquet(target)

            if df.isEmpty():
                print(f"WARNING: table '{table.get('name')}' is empty")
        
        except Exception as e:
            raise RuntimeError(
                f"Failed to read S3 path for table '{table.get('name')}': {table.get('target')}"
            ) from e

        data_from_s3_raw[table.get('name')] = df

    return data_from_s3_raw