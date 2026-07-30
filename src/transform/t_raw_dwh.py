import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / 'extract'))

from e_from_raw import extract_data_from_raw

def transform_data_from_raw_to_dwh(dataframes_raw = extract_data_from_raw()):
    
    try:
        dataframes_transformed = {}

        for table_name, datas in dataframes_raw.items():

            df_transformed = datas.copy()

            for col in df_transformed.columns:
                if 'id' in col.lower():
                    # принудительное преобразования в int. безопасный int с поддержкой пропусков NaN (тип Int64 с большой буквы)
                    df_transformed[col] = pd.to_numeric(df_transformed[col], errors='coerce').astype('Int64')
                    df_transformed = df_transformed.dropna(subset=[col])
                elif 'date' in col.lower():
                    df_transformed[col] = pd.to_datetime(df_transformed[col], format = '%d.%m.%Y', errors='coerce')
                    df_transformed[col] = df_transformed[col].fillna(pd.Timestamp('1900-01-01'))
                elif 'amount' in col.lower():
                    df_transformed[col] = pd.to_numeric(df_transformed[col], errors='coerce').astype(float)

            df_transformed['loaded_at'] = pd.Timestamp.now()
                
            dataframes_transformed[table_name] = df_transformed

        return dataframes_transformed
    
    except Exception as error:
        print(f'Ошибка при трансформации: {error}')