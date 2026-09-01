import yaml
from pathlib import Path
from pyspark.sql import SparkSession

def load_config():
    config_path = Path(__file__).parent.parent / 'config.yaml'
    with open(config_path, 'r', encoding='UTF-8') as file:
        config = yaml.safe_load(file)
    return config

CONFIG = load_config()

def get_spark_session():
    # .config("spark.driver.memory", "2g") - гб на управляющий процесс (Driver), который собирает итоговые данные
    # .config("spark.driver.maxResultSize", "1g") - ограничивает объем данных, который можно выгрузить в память ноутбука, страхуя систему от падения

    driver_path = Path(__file__).parent / "drivers" / "postgresql-42.7.13.jar"
    
    if not driver_path.exists():
        raise FileNotFoundError(f"Драйвер не найден: {driver_path}")
    
    print(f"✅ Драйвер найден: {driver_path}")

    spark = SparkSession.builder \
        .appName("SparkApp") \
        .master("local[2]") \
        .config("spark.driver.memory", "2g") \
        .config("spark.executor.memory", "1g") \
        .config("spark.sql.shuffle.partitions", "2") \
        .config("spark.driver.maxResultSize", "1g") \
        .config("spark.jars", Path(__file__).parent / "drivers" / "postgresql-42.7.13.jar") \
        .getOrCreate()

    return spark

# возвращает параметры для подключения к PostgreSQL
def get_jdbc_options(db_name):
    for db in CONFIG['database']:
        if db_name == db['name']:
            pg = db['connection']

            return {
                "url": f"jdbc:postgresql://{pg['host']}:{pg['port']}/{db_name}",
                "user": pg['user'],
                "password": pg['password'],
                "driver": "org.postgresql.Driver"
            }
    raise ValueError(f"База данных {db_name} не найдена")

def get_db_config(db_name: str):
    for db in CONFIG['database']:
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
                    'file': table.get('file')
                })

    return tables

def get_table_names(db_name: str, schema_name: str):
    return [t['name'] for t in get_all_tables(db_name, schema_name)]