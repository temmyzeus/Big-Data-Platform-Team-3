from datetime import datetime, timedelta

# import boto3
# from airflow.models import Variable
from typing import Any
from airflow.providers.amazon.aws.operators.emr import (
    EmrAddStepsOperator, EmrCreateJobFlowOperator, EmrTerminateJobFlowOperator)
from airflow.providers.amazon.aws.sensors.emr import EmrStepSensor

from airflow import DAG


# def aws_session():
#     session = boto3.Session(
#                     aws_access_key_id=Variable.get('access_key'),
#                     aws_secret_access_key=Variable.get('secret_key'),
#                     region_name="us-east-1"
#     )
#     return session

# def boto3_client(aws_service):

#     client = boto3.client(aws_service,
#                           aws_access_key_id=Variable.get('access_key'),
#                           aws_secret_access_key=Variable.get('secret_key'),
#                           region_name="us-east-1")

    # return client


JOB_FLOW_OVERRIDES: dict[str, Any] = {
    "Name": "Spark Job Cluster",
    "ReleaseLabel": "emr-5.20.0",
    "Applications": [{"Name": "Spark"}],
    "LogUri": "s3://big-data-platform-team-3/emr_logs/",
    "Instances": {
        "InstanceGroups": [
            {
                "Name": "Primary node",
                "Market": "ON_DEMAND",
                "InstanceRole": "MASTER",
                "InstanceType": "m5.xlarge",
                "InstanceCount": 1,
            },
            {
                'Name': 'Worker nodes',
                'Market': 'ON_DEMAND',
                'InstanceRole': 'CORE',
                'InstanceType': 'm5.xlarge',
                'InstanceCount': 1,
                }
        ],
        # If the EMR steps complete too quickly the cluster will be torn down before the other system test
        # tasks have a chance to run (such as the modify cluster step, the addition of more EMR steps, etc).
        # Set KeepJobFlowAliveWhenNoSteps to False to avoid the cluster from being torn down prematurely.
        "KeepJobFlowAliveWhenNoSteps": True,
        "TerminationProtected": False,
    },
    # "Steps": SPARK_STEPS,
    "JobFlowRole": "emr-instance-profile",
    "ServiceRole": "emr-service-role",
}

SPARK_STEPS = [
    {
        'Name': 'Run PySpark ETL',
        'ActionOnFailure': 'TERMINATE_CLUSTER',
        'HadoopJarStep': {
            'Jar': 'command-runner.jar',
            'Args': [
                'spark-submit',
                '--deploy-mode', 'cluster',
                '--master', 'yarn',
                's3://big-data-platform-team-3/emr_pyspark/pyspark.py',
                '--input', 's3://big-data-platform-team-3/etl/car_sales_data.parquet',
                '--output', 's3://big-data-platform-team-3/output'
            ]
        }
    }
]



with DAG(
    dag_id="emr_orchestration",
    start_date=datetime(2025, 4, 23),
    schedule_interval='0 0 * * *',
    catchup=False
) as dag:
    create_emr_cluster = EmrCreateJobFlowOperator(
    task_id='create_emr_cluster',
    job_flow_overrides=JOB_FLOW_OVERRIDES,
    aws_conn_id='aws_default',
    region_name='us-east-1', 
    dag=dag
)
    add_steps = EmrAddStepsOperator(
    task_id='add_steps',
    job_flow_id="{{ task_instance.xcom_pull(task_ids='create_emr_cluster', key='return_value') }}",
    aws_conn_id='aws_default',
    steps=SPARK_STEPS,
    dag=dag
)

step_checker = EmrStepSensor(
    task_id='watch_step',
    job_flow_id="{{ task_instance.xcom_pull('create_emr_cluster', key='return_value') }}",
    step_id="{{ task_instance.xcom_pull(task_ids='add_steps', key='return_value')[0] }}",
    aws_conn_id='aws_default',
    dag=dag
)

terminate_cluster = EmrTerminateJobFlowOperator(
    task_id='terminate_cluster',
    job_flow_id="{{ task_instance.xcom_pull(task_ids='create_emr_cluster', key='return_value') }}",
    aws_conn_id='aws_default',
    dag=dag
)

create_emr_cluster >> add_steps >> step_checker >> terminate_cluster