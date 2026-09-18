import sys
from pathlib import Path
from pyspark.sql import DataFrame

sys.path.append(str(Path(__file__).parent.parent.parent / 'infrastructure' / 'database'))

from postgres import get_jdbc_options

def get_load_transformed_data_from_s3_to_postgres_ods(config: dict, data_from_s3_raw_transformed: dict):
    options = get_jdbc_options(config, 'dwh')

    if not isinstance(data_from_s3_raw_transformed, dict):
        raise TypeError (f"The second arg is not dict")

    if not data_from_s3_raw_transformed:
        raise ValueError (f"The second arg is empty")

    for table_name, df in data_from_s3_raw_transformed.items():

        if not isinstance(table_name, str):
            raise TypeError (f"Invalid table name: {table_name}")
        
        if not isinstance(df, DataFrame):
            raise TypeError (f"Invalid DataFrame for table {table_name}")
        
        if not table_name.strip():
            raise ValueError (f"Key (table) with table name {table_name} does not exist")

        df.write \
            .format("jdbc") \
            .mode("overwrite") \
            .options(**options) \
            .option('dbtable', 'staging.temp_' + table_name) \
            .save()