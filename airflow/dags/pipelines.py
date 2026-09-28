from datetime import datetime, timedelta
from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator

SPARK_SUBMIT = '/mnt/d/pet/.wsl_venv/bin/spark-submit'
DBT = '/mnt/d/pet/.wsl_venv/bin/dbt'

SPARK_OPTIONS_PACKAGES = "--packages org.apache.hadoop:hadoop-aws:3.5.0,org.slf4j:slf4j-simple:2.0.16"
SPARK_OPTIONS_PACKAGES_JARS = f"{SPARK_OPTIONS_PACKAGES} --jars /mnt/d/pet/src/drivers/postgresql-42.7.13.jar"

default_args = {
    "owner": "admin",
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

with DAG (
    dag_id='pipelines',
    start_date=datetime(2026, 9, 27),
    schedule="47 15 * * *",
    catchup=False,
    default_args=default_args,
    tags=['pet'],
) as dag:
    
    get_el_from_disk_to_s3_raw = BashOperator(task_id='el_from_disk_to_s3_raw',
        bash_command=f"cd /mnt/d/pet && source ./.wsl_venv/bin/activate && {SPARK_SUBMIT} {SPARK_OPTIONS_PACKAGES} /mnt/d/pet/src/pipelines/from_disk_to_raw.py")

    get_etl_from_s3_raw_to_postgres_staging = BashOperator(task_id='etl_from_s3_raw_to_postgres_staging',
        bash_command=f"cd /mnt/d/pet && source ./.wsl_venv/bin/activate && {SPARK_SUBMIT} {SPARK_OPTIONS_PACKAGES_JARS} /mnt/d/pet/src/pipelines/from_raw_to_staging.py")

    dbt_ods = BashOperator(task_id='dbt_ods',
        bash_command=f"cd /mnt/d/pet/dbt_project && source /mnt/d/pet/.wsl_venv/bin/activate && {DBT} run --select ods")

    dbt_dds = BashOperator(task_id='dbt_dds',
        bash_command=f"cd /mnt/d/pet/dbt_project && source /mnt/d/pet/.wsl_venv/bin/activate && {DBT} run --select dds")

    dbt_dm = BashOperator(task_id='dbt_dm',
        bash_command=f"cd /mnt/d/pet/dbt_project && source /mnt/d/pet/.wsl_venv/bin/activate && {DBT} run --select dm")

    get_el_from_disk_to_s3_raw >> get_etl_from_s3_raw_to_postgres_staging >> dbt_ods >> dbt_dds >> dbt_dm