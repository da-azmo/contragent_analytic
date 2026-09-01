from pyspark.sql import SparkSession
import sys
from pathlib import Path

sys_path = Path(__file__).parent.parent
sys.path.append(str(sys_path))

from db_utils import get_all_tables, get_jdbc_options

def extract_from_raw(spark: SparkSession):
    dataframes = {}
    tables = get_all_tables('raw', 'datas')

    for table_info in tables:
        table_name = table_info['name']

        options = get_jdbc_options('raw')
        options['dbtable'] = table_name

        df = spark.read \
            .format('jdbc') \
            .options(**options) \
            .load()

        dataframes[table_name] = df
        print(f"Extracted {table_name} ({df.count()} rows)")

    return dataframes