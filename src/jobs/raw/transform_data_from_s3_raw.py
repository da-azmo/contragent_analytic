import sys
from pathlib import Path
from pyspark.sql.functions import to_date, col, current_timestamp, coalesce, lit, md5, concat_ws

sys.path.append(str(Path(__file__).parent.parent.parent / 'core'))
sys.path.append(str(Path(__file__).parent.parent.parent))

from metadata import get_postgres_all_tables
from type_mapping import parse_type

def get_transform_data_from_s3_raw(config: dict, data_from_s3_raw: dict):
    data_from_s3_raw_transformed = {}
    tables = get_postgres_all_tables(config, 'dwh', 'ods')
    tables_name_dtype = {table['name'] : table['dtype'] for table in tables}
    tables_name_not_null = {table['name'] : table.get('not_null', []) for table in tables}

    for table_name, datas in data_from_s3_raw.items():

        if table_name in tables_name_dtype:
            df = datas # создание нового DataFrame с теми же данными, что и datas. Spark DataFrame иммутабелен
            set_df_not_null_columns = set()
            dtypes = tables_name_dtype[table_name]
            set_not_null = set(tables_name_not_null[table_name])
            columns_expected = set([column.lower() for column in dtypes])
            hash_columns = []

            unexpected_columns = set(col.lower() for col in df.columns) - columns_expected

            if unexpected_columns:
                raise ValueError (f"Unexpected columns: {unexpected_columns}")

            for column_name, column_type in dtypes.items():

                if column_name in df.columns:
                    if column_type.lower() == 'datetype':
                        df = df.withColumn(column_name, to_date(col(column_name), format="dd.MM.yyyy"))
                    
                    else:
                        target_type = parse_type(column_type)
                        df = df.withColumn(column_name, col(column_name).cast(target_type))

                    if column_name in set_not_null:
                        set_df_not_null_columns.add(column_name)

                    if column_name != 'id' and column_name != 'loaded_at':
                        hash_columns.append(column_name)
            
            if set_df_not_null_columns < set_not_null:
                raise ValueError (f"Missing columns {set_not_null - set_df_not_null_columns} in dataframe {table_name}")
            
            df = df.dropna(subset=list(set_not_null))
            
            hash_columns = [coalesce(col(c).cast('string'), lit('<NULL>')) for c in hash_columns]
            df = df.withColumn('hashdiff', md5(concat_ws('|', *hash_columns)))
            df = df.withColumn('loaded_at', current_timestamp())
            

            data_from_s3_raw_transformed[table_name] = df

    return data_from_s3_raw_transformed