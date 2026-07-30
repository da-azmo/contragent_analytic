import pandas as pd
import sys
from pathlib import Path

src_path = Path(__file__).parent.parent
sys.path.append(str(src_path))

from db_utils import create_engine_for_db, get_schema_config

try:
    engine = create_engine_for_db('raw')
    config_schema = get_schema_config('raw', 'datas')

    for table in config_schema['tables']:
        file = pd.read_csv(table['file'], encoding='UTF-8', sep=';')
        file.to_sql(table['name'], engine, schema=config_schema['name'], if_exists='append', index=False)

except Exception as error:
    print(f'Ошибка при работе PostgreSQL: {error}')
finally:
    print("Соединение закрыто")