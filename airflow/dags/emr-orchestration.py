from datetime import datetime, timedelta

from airflow.providers.amazon.aws.operators.emr import (
    EmrAddStepsOperator, EmrCreateJobFlowOperator, EmrTerminateJobFlowOperator)
from airflow.providers.amazon.aws.sensors.emr import EmrStepSensor

from airflow import DAG

with DAG(
    dag_id="emr_orchestration",
    start_date=datetime(2024, 11, 22),
    schedule_interval='0 0 * * *',
    catchup=False
) as dag: