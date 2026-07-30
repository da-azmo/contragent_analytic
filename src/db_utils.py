import yaml
from sqlalchemy import create_engine
import sys
from pathlib import Path
from typing import Dict, List, Any

def load_config():
    config_path = Path(__file__).parent.parent / 'config.yaml'
    with open(config_path, 'r', encoding='UTF-8') as file:
        config = yaml.safe_load(file)
    return config


CONFIG = load_config()


def get_database_config(db_name: str):
    for db in CONFIG['database']:
        if db['name'] == db_name:
            return db
    return None


def get_schema_config(db_name: str, sch_name: str):
    db_config = get_database_config(db_name)

    if not db_config:
        raise ValueError(f'База данных {db_name} не найдена')
    
    schemas_list_config = db_config['schemas']

    for sch in schemas_list_config:
        if sch['name'] == sch_name:
            return sch
    return None


def get_tables_config(db_name: str, sch_name: str, table_name: str):
    sch_config = get_schema_config(db_name, sch_name)

    if not sch_config:
        raise ValueError(f'Схема {sch_name} не найдена')

    tables_list_config = sch_config['tables']

    for tbl in tables_list_config:
        if tbl['name'] == table_name:
            return tbl
    return None


def create_engine_for_db(db_name: str):
    db_config = get_database_config(db_name)

    if not db_config:
        raise ValueError(f'База данных {db_name} не найдена')

    conn = db_config['connection']
    engine_string = f"postgresql://{conn['user']}:{conn['password']}@{conn['host']}:{conn['port']}/{db_name}"
    
    return create_engine(engine_string)