from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp, to_date
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from db_utils import get_all_tables
from type_mapping import parse_type

def transform_data_from_raw_to_dwh (spark: SparkSession, dataframes: list):
    dataframes_transformed = {}

    tables = get_all_tables('dwh', 'ods')
    tables_dtype = {table['name']: table['dtype'] for table in tables}

    for table_name, datas in dataframes.items():
        df = datas.select('*')

        if table_name in tables_dtype:
            dtypes = tables_dtype[table_name]

            for column_name, type_str in dtypes.items():

                if type_str.lower() == 'datetype':
                    df = df.withColumn(column_name, to_date(col(column_name), 'dd.MM.yyyy'))

                elif column_name == 'loaded_at':
                    df = df.withColumn(column_name, current_timestamp())

                elif column_name in df.columns:
                    target_type = parse_type(type_str)
                    df = df.withColumn(column_name, col(column_name).cast(target_type))

        dataframes_transformed[table_name] = df

    return dataframes_transformed