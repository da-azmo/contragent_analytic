import yaml
import os
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from pyspark.sql import SparkSession

load_dotenv()

def load_config():
    config_path = Path(__file__).parent.parent / 'config.yaml'
    with open(config_path, 'r', encoding='UTF-8') as file:
        config = yaml.safe_load(file)
    return config

CONFIG = load_config()

def get_drivers():
    try:
        minio_packages = ("org.apache.hadoop:hadoop-aws:3.5.0", "org.apache.hadoop:hadoop-aws:3.5.0,org.slf4j:slf4j-simple:2.0.16")
        postgres_jar_package = Path(__file__).parent / "drivers" / "postgresql-42.7.13.jar"

        if not postgres_jar_package.exists():
            raise FileNotFoundError(
                f"PostgreSQL JDBC драйвер не найден по пути: {postgres_jar_package}")

        print(f"✅ Драйвер PostgreSQL найден: {postgres_jar_package}")
        print(f"✅ MinIO пакеты: {minio_packages}")

        return minio_packages, str(postgres_jar_package)
    
    except Exception as e:
        raise FileNotFoundError(f"Драйвер не найден") from e

def get_spark_session():
    # .config("spark.driver.memory", "2g") - гб на управляющий процесс (Driver), который собирает итоговые данные
    # .config("spark.driver.maxResultSize", "1g") - ограничивает объем данных, который можно выгрузить в память ноутбука, страхуя систему от падения
    # .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") - реализация интерфейса FileSystem для S3. Без этой настройки Spark не поймет, что делать с путями типа s3a://bucket/file.csv.

    minio_packages, postgres_jar_package = get_drivers()

    spark = SparkSession.builder \
        .appName("SparkApp") \
        .master("local[2]") \
        .config("spark.driver.memory", "2g") \
        .config("spark.executor.memory", "1g") \
        .config("spark.sql.shuffle.partitions", "2") \
        .config("spark.driver.maxResultSize", "1g") \
        .config("spark.jars", postgres_jar_package) \
        .config("spark.jars.packages", minio_packages) \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
        .config("spark.hadoop.fs.s3a.access.key", os.getenv("MINIO_ACCESS_KEY_RAW")) \
        .config("spark.hadoop.fs.s3a.secret.key", os.getenv("MINIO_SECRET_KEY_RAW")) \
        .config("spark.hadoop.fs.s3a.endpoint", os.getenv("MINIO_ENDPOINT_RAW")) \
        .getOrCreate()

    return spark

# возвращает параметры для подключения к PostgreSQL
def get_jdbc_options(db_name):
    for db in CONFIG['layers']:
        if db_name == db['name']:
            pg = db['connection']

            host = os.getenv(pg['host'].strip('${}'), '')
            port = os.getenv(pg['port'].strip('${}'), '')
            user = os.getenv(pg['user'].strip('${}'), '')
            password = os.getenv(pg['password'].strip('${}'), '')

            missing = []
            
            if not host: missing.append('host')
            if not port: missing.append('port')
            if not user: missing.append('user')
            if not password: missing.append('password')

            if missing:
                raise ValueError(f"Отсутствуют переменные окружения для {db_name}: {', '.join(missing)}")

            return {
                "url": f"jdbc:postgresql://{host}:{port}/{db_name}",
                "user": user,
                "password": password,
                "driver": "org.postgresql.Driver"
            }

    raise ValueError(f"JDBC-конфиг для {db_name} не найден")

def get_db_config(db_name: str):
    for db in CONFIG['layers']:
        if db['name'] == db_name:
            return db
    raise ValueError(f"База данных {db_name} не найдена")

def get_all_tables(db_name: str, schema_name: str):
    db_config = get_db_config(db_name)
    tables = []

    for schema in db_config.get('schemas', []):
        if schema['name'] == schema_name:
            for table in schema.get('tables', []):
                tables.append({
                    'schema': schema['name'],
                    'name': table['name'],
                    'full_name': f"{schema['name']}.{table['name']}",
                    'dtype': table.get('dtype', None)
                })
        break

    return tables

def get_table_names(db_name: str, schema_name: str):
    return [t['name'] for t in get_all_tables(db_name, schema_name)]

def get_file_target(db_name: str, schema_name: str, table_name: str):
    execution_date = datetime.now().strftime("%Y-%m-%d")
    file, target = str(), str()
    db_config = get_db_config(db_name)

    for schema in db_config.get('schemas', []):
        if schema['name'] == schema_name:

            for table in schema.get('tables', []):
                if table['name'] == table_name:

                    file = table.get('file', '')

                    target = table.get('target', '') \
                        .format(execution_date=execution_date)

                    break

    if not target and not file:
        raise ValueError(f"Отсутствуют входящий и выходящий файлы {db_name}")
    
    return file, target