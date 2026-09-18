import os
from datetime import datetime


# returns the database
def get_database_config(config: dict, layer_name: str):
    for layer in config['layers']:
        if layer['name'] == layer_name:
            return layer
    
    raise ValueError (f"Layer {layer_name} not found in this config")




# returns all schemas from Postgres
def get_postgres_all_schemas(config: dict, layer_name: str):
    db_config = get_database_config(config, layer_name)
    schemas = []

    if 'schemas' not in db_config:
        raise ValueError (f"Config for {layer_name} has no 'schemas'")

    for schema in db_config['schemas']:
        schemas.append({
            'name': schema.get('name'),
            'tables': schema.get('tables', [])})

    return schemas




# returns all tables from Postgres
def get_postgres_all_tables(config: dict, layer_name: str, schema_name: str):
    sch_config = get_postgres_all_schemas(config, layer_name)

    for schema in sch_config:
        if schema['name'] == schema_name:
            if 'tables' not in schema:
                raise ValueError (f"Layer '{layer_name}' schema '{schema_name}' has no 'tables'") 

            return [
                {
                    'schema': schema['name'],
                    'name': table['name'],
                    'full_name': f"{schema['name']}.{table['name']}",
                    'dtype': table.get('dtype', None),
                    'not_null': table.get('not_null', None),
                }
            for table in schema.get('tables')]

    raise ValueError(f"Schema '{schema_name}' not found in layer '{layer_name}'")




# returns all tables from s3
def get_s3_all_tables(config: dict, layer_name: str):
    db_config = get_database_config(config, layer_name)
    if 'tables' not in db_config:
        raise ValueError (f"Layer '{layer_name}' has no 'tables' in this config")

    tables = []

    for table in db_config['tables']:
        file, target = get_file_target(config, layer_name, table.get('name'))

        tables.append({
            'name': table['name'],
            'file': file,
            'target': target
        })

    if not tables:
            raise ValueError("No tables found in 'raw' layer")
    
    return tables




# returns the names of all tables from Postgres
def get_postgres_table_names(config: dict, layer_name: str, schema_name: str):
    return [t['name'] for t in get_postgres_all_tables(config, layer_name, schema_name)]




# returns the names of all tables from s3
def get_s3_table_names(config: dict, layer_name: str):
    return [t['name'] for t in get_s3_all_tables(config, layer_name)]




# returns the file and the target object for s3
def get_file_target(config: dict, layer_name: str, table_name: str):
    execution_date = datetime.now().strftime("%Y-%m-%d")
    
    db_config = get_database_config(config, layer_name)
    if 'tables' not in db_config:
        raise ValueError (f"Layer '{layer_name}' has no 'tables'")

    for table in db_config['tables']:
        if table['name'] == table_name:

            file = table.get('file', '')

            target = table.get('target', '') \
                .format(execution_date=execution_date)

            if not target and not file:
                raise ValueError (f"Layer {layer_name} table {table_name} has no file and target in this config")
        
            if not target:
                raise ValueError (f"Layer {layer_name} table {table_name} has no target in this config")

            if not file:
                raise ValueError (f"Layer {layer_name} table {table_name} has no file in this config")

            return file, target

    raise ValueError (f"Table '{table_name}' does not found in layer '{layer_name}' in this config")