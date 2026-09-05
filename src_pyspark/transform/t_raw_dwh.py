from pyspark.sql import SparkSession
import pyspark.sql.functions as F
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from db_utils import get_all_tables
from type_mapping import parse_type

def transform_data_from_raw_to_dwh (spark: SparkSession, dataframes: dict):
    dataframes_transformed = {}

    tables = get_all_tables('dwh', 'ods')
    tables_dtype = {table['name']: table['dtype'] for table in tables}

    for table_name, datas in dataframes.items():
        df = datas.select('*')

        if table_name in tables_dtype:
            dtypes = tables_dtype[table_name]

            for column_name, type_str in dtypes.items():

                if type_str.lower() == 'datetype':
                    df = df.withColumn(column_name, F.to_date(F.col(column_name), 'dd.MM.yyyy'))
                    

                elif column_name == 'loaded_at':
                    df = df.withColumn(column_name, F.current_timestamp())

                elif column_name in df.columns:
                    target_type = parse_type(type_str)
                    df = df.withColumn(column_name, F.col(column_name).cast(target_type))

                df = df.dropna()

        dataframes_transformed[table_name] = df
    
    return dataframes_transformed