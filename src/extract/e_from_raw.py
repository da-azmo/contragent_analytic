import pandas as pd
import sys
from pathlib import Path

# __file__ — это встроенная магическая переменная в Python, которая хранит полный путь к текущему файлу, в котором она написана.

src_path = Path(__file__).parent.parent
sys.path.append(str(src_path))

from db_utils import create_engine_for_db, get_schema_config

def extract_data_from_raw():

    try:
        with create_engine_for_db('raw').connect() as conn:
            dataframes = {}

            config_sch = get_schema_config('raw', 'datas')

            for table in config_sch['tables']:
                key = f'{table['name']}'
                dataframes[key] = pd.read_sql(f'select * from {table['name']}', conn)
            return dataframes

    except Exception as error:
        print(f'При чтении данных из таблицы {table['name']} произошла ошибка: {error}')
        return None