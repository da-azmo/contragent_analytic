from pathlib import Path
import sys
from pyspark.sql import SparkSession

src_path = Path(__file__).parent.parent
sys.path.append(str(src_path))

from db_utils import get_file_target, get_table_names

def generate_datas(spark: SparkSession):
    try:
        tables = get_table_names('raw', 'datas')

        for table in tables:
            file, target = get_file_target('raw', 'datas', table)

            df = spark.read \
                .option("header", "true") \
                .option("delimiter", ";") \
                .csv(file)

            if df: print('Чтение файлов выполнено успешно')
            
            df.write \
                .format("parquet") \
                .mode("append") \
                .save(target)

    except Exception as error:
        print(f'Ошибка при работе GENERATE: {error}')