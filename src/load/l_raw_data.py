import pandas as pd
import sys
from pathlib import Path
from sqlalchemy import text

sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / 'transform'))

from db_utils import create_engine_for_db, get_schema_config
from t_raw_dwh import transform_data_from_raw_to_dwh

def load_data_to_dwh():

    try:
        dataframes_transformed = transform_data_from_raw_to_dwh()
        config_schema = get_schema_config('dwh', 'ods')
        config_tables = config_schema['tables']

        for table in config_tables:

            df = dataframes_transformed[table['name']]

            if df.empty:
                raise Exception ('Невалидные данные')

            columns = list(table['dtype'].keys())
            columns_string = ', '.join(columns)

            placeholder = ', '.join(f':{col}' for col in columns)

            update_columns = list(col for col in columns if col != table['pk'])
            set_clause = ', '.join(f'{col} = EXCLUDED.{col}' for col in update_columns)

            query = f'''INSERT INTO {config_schema['name']}.{table['name']} ({columns_string})
                        VALUES ({placeholder})
                        ON CONFLICT ({table['pk']}) DO UPDATE SET {set_clause};'''

            df_to_insert = df[columns] #новый DataFrame, который содержит только указанные колонки
            df_to_insert = df_to_insert.where(pd.notnull(df_to_insert), None)

            records = df_to_insert.to_dict(orient='records')

            with create_engine_for_db('dwh').connect() as conn:
                conn.execute(text(query), records)
                conn.commit()

    except Exception as error:
        print(f'Ошибка: {error}')