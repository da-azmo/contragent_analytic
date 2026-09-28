import subprocess # стандартный модуль Python, который позволяет запускать внешние программы и команды операционной системы
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
SPARK_SUBMIT = PROJECT_ROOT / '.wsl_venv' / 'bin' / 'spark-submit'

def run_spark():
    subprocess.run([
        str(SPARK_SUBMIT),
        "--packages",
        "org.apache.hadoop:hadoop-aws:3.5.0,org.slf4j:slf4j-simple:2.0.16",
        "--jars",
        "/mnt/d/pet/src/drivers/postgresql-42.7.13.jar",
        "./src/pipelines/run.py"
    ],
    check=True)

def run_dbt_ods():
    subprocess.run([
        "dbt",
        "run",
        "--select",
        "ods"
    ],
    cwd="./dbt_project",
    check=True)

def run_dbt_staging():
    subprocess.run([
        "dbt",
        "run",
        "--select",
        "stg_from_ods_to_dds_companies",
        "stg_from_ods_to_dds_contracts"
    ],
    cwd="./dbt_project",
    check=True)

def run_dbt_snapshot():
    subprocess.run([
        "dbt",
        "snapshot"
    ],
    cwd="./dbt_project",
    check=True)

def run_dbt_dds():
    subprocess.run([
        "dbt",
        "run",
        "--select",
        "dds"
    ],
    cwd="./dbt_project",
    check=True)

def run_dbt_dm():
    subprocess.run([
        "dbt",
        "run",
        "--select",
        "dm"
    ],
    cwd="./dbt_project",
    check=True)

if __name__ == "__main__":
    run_spark()
    run_dbt_ods()
    run_dbt_staging()
    run_dbt_snapshot()
    run_dbt_dds()
    run_dbt_dm()