from pyspark.sql import SparkSession
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / 'transform'))

from db_utils import get_jdbc_options
from t_raw_dwh import transform_data_from_raw_to_dwh

def load_data_to_dwh(spark: SparkSession, dataframes_transformed: dict):
    try:
        options = get_jdbc_options('dwh')

        for table_name, df in dataframes_transformed.items():

            df.write \
                .format('jdbc') \
                .options(**options) \
                .option('dbtable', f'temp_{table_name}') \
                .mode("overwrite") \
                .save()

            columns = df.columns
            string_columns = ', '.join(columns)
            set_clause = ', '.join(f'{col} = EXCLUDED.{col}' for col in columns)
            
            query = f"""
                INSERT INTO ods.{table_name} ({string_columns})
                SELECT {string_columns} FROM temp_{table_name}
                ON CONFLICT (id) DO UPDATE SET {set_clause}
            """

            conn = spark._jvm.java.sql.DriverManager.getConnection(
                options['url'],
                options['user'],
                str(options['password'])
            )

            try:
                stmt = conn.createStatement()
                stmt.execute(query)
                stmt.execute(f"DROP TABLE temp_{table_name}")
                conn.commit()
            finally:
                conn.close()

            print(f"✅ UPSERT выполнен для ods.{table_name}")

    except Exception as error:
        raise RuntimeError(f"❌ Ошибка при записи данных в таблицу: {error}") from error