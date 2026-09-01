from pathlib import Path
import sys
from pyspark.sql import SparkSession

src_path = Path(__file__).parent.parent
sys.path.append(str(src_path))

from db_utils import get_all_tables, get_jdbc_options

def generate_datas(spark: SparkSession):
    try:
        tables = get_all_tables('raw', 'datas')

        options = get_jdbc_options('raw')

        for table in tables:
            options['dbtable'] = 'datas.' + table['name']

            df = spark.read \
                .option("header", "true") \
                .option("delimiter", ";") \
                .csv(table['file'])
            
            df.write \
                .format("jdbc") \
                .options(**options) \
                .mode("append") \
                .save()

    except Exception as error:
        print(f'Ошибка при работе PostgreSQL GENERATE: {error}')