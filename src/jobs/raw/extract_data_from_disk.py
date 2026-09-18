from pathlib import Path
import sys
from pyspark.sql import SparkSession

src_path = Path(__file__).parent.parent.parent / 'core'
sys.path.append(str(src_path))

from metadata import get_s3_all_tables

def get_extract_data_from_disk (spark: SparkSession, config: dict):
    try:
        tables = get_s3_all_tables(config, 'raw')

        data_from_disk = {}

        for table in tables:
            file_path = table.get('file')

            df = spark.read \
                .option("header", "true") \
                .option("delimiter", ";") \
                .csv(f"{file_path}.csv")

            data_from_disk[table.get('name')] = {
                'target': table.get('target'),
                'df': df,
            }

        return data_from_disk

    except Exception as error:
        raise RuntimeError(f'Reading the tables has not been completed in this config') from error