import os, sys
from datetime import timedelta

from airflow import DAG, settings
from airflow.models.connection import Connection
from airflow.models.xcom import XCom
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor
from airflow.providers.amazon.aws.transfers.local_to_s3 import LocalFilesystemToS3Operator
from airflow.utils.db import provide_session

from etl.generate import generate_listing, gen_user
from etl.utils import generate_data

print(f"PYTHONPATH: {sys.path}")

LOCAL_DATA_PATH: str = "data"
DAG_NAME: str = "data-generation"

@provide_session
def create_file_connection(session=None):
    conn_id = "fs_default"
    file_path = "data/"

    # Check if it already exists
    existing_conn = session.query(Connection).filter(Connection.conn_id == conn_id).first()
    if existing_conn:
        print(f"Connection '{conn_id}' already exists.")
        return

    # Create new connection
    new_conn = Connection(
        conn_id=conn_id,
        conn_type="fs",  # Must match the correct Airflow connection type
        extra={"path": file_path}
    )

    session.add(new_conn)
    session.commit()
    print(f"Connection '{conn_id}' created with path '{file_path}'.")

# Call this function at DAG startup or in a setup script
create_file_connection()

with DAG(
    dag_id=DAG_NAME,
    schedule_interval=None,
    start_date=None,
    catchup=False,
    default_args={
        "owner": "airflow",
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    },
) as dag:
    
    generate_user_data = PythonOperator(
        task_id="generate_user_data",
        python_callable=generate_data,
        op_kwargs={
            "data_gen_func": gen_user,
            "num_rows": 5_000,
            "output_path": os.path.join(LOCAL_DATA_PATH, "user_data.parquet"),
        },
    )

    generate_listing_data = PythonOperator(
        task_id="generate_listing_data",
        python_callable=generate_data,
        op_kwargs={
            "data_gen_func": generate_listing,
            "num_rows": 5_000,
            "output_path": os.path.join(LOCAL_DATA_PATH, "listing_data.parquet"),
        },
    )

    generate_transaction_data = EmptyOperator(
        task_id="generate_transaction_data"
    )

    detect_new_data_files = FileSensor(
        task_id="detect_new_data_files",
        filepath="*.parquet",
        recursive=False,
        mode="poke",
        poke_interval=60
    )

    
    upload_to_s3 = LocalFilesystemToS3Operator(
        task_id="upload_to_s3",
        filename=[1,2,3],
        dest_key="...",
        dest_bucket="..."
    )

    generate_user_data >> [generate_listing_data, generate_transaction_data]

    detect_new_data_files >> upload_to_s3
