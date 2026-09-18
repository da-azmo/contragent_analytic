from pyspark.sql import SparkSession
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / 'storage'))

from minio import get_s3_connection_options

def get_spark_session():
    # .config("spark.driver.memory", "2g") - гб на управляющий процесс (Driver), который собирает итоговые данные
    # .config("spark.driver.maxResultSize", "1g") - ограничивает объем данных, который можно выгрузить в память ноутбука, страхуя систему от падения
    # .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") - реализация интерфейса FileSystem для S3. Без этой настройки Spark не поймет, что делать с путями типа s3a://bucket/file.

    s3_connection_options = get_s3_connection_options()

    spark = SparkSession.builder \
        .appName("SparkApp") \
        .master("local[2]") \
        .config("spark.driver.memory", "2g") \
        .config("spark.executor.memory", "1g") \
        .config("spark.sql.shuffle.partitions", "2") \
        .config("spark.driver.maxResultSize", "1g") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
        .config("spark.hadoop.fs.s3a.access.key", s3_connection_options.get('access_key')) \
        .config("spark.hadoop.fs.s3a.secret.key", s3_connection_options.get('secret_key')) \
        .config("spark.hadoop.fs.s3a.endpoint", s3_connection_options.get('endpoint')) \
        .getOrCreate()

    if not spark:
        raise RuntimeError (f"Failed to create Spark session")

    return spark