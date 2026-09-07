import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / "extract"))
sys.path.append(str(Path(__file__).parent.parent / "transform"))
sys.path.append(str(Path(__file__).parent.parent / "load"))

from db_utils import get_spark_session
from generate_data import generate_datas
from e_from_raw import extract_from_raw
from t_raw_dwh import transform_data_from_raw_to_dwh
from l_raw_data import load_data_to_dwh

def main():
    print("Запуск")

    spark = get_spark_session()

    try:
        print("Generate")
        generate_datas(spark)

        print("Extract")
        extract = extract_from_raw(spark)

        print("Transform")
        dataframes_transformed = transform_data_from_raw_to_dwh(spark, extract)

        print("Load")
        load_data_to_dwh(spark, dataframes_transformed)

        print("Gone")

    except Exception as e:
        print(f"Ошибка: {e}")
        raise
    
    finally:
        spark.stop()

if __name__ == "__main__":
    main()