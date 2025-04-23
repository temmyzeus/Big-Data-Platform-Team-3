from datetime import datetime, timedelta
from typing import Any
from airflow.providers.amazon.aws.operators.emr import (
    EmrAddStepsOperator, EmrCreateJobFlowOperator, EmrTerminateJobFlowOperator)
from airflow.providers.amazon.aws.sensors.emr import EmrStepSensor
from airflow import DAG

JOB_FLOW_OVERRIDES: dict[str, Any] = {
    "Name": "Spark Job Cluster",
    "ReleaseLabel": "emr-5.20.0",
    "Applications": [{"Name": "Spark"}],
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
        "KeepJobFlowAliveWhenNoSteps": True,
        "TerminationProtected": False,
    },
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
    # Define AWS hook parameters to include region
    aws_hook_params = {"region_name": "us-east-1"}
    
    create_emr_cluster = EmrCreateJobFlowOperator(
        task_id='create_emr_cluster',
        job_flow_overrides=JOB_FLOW_OVERRIDES,
        aws_conn_id='aws_default',
        aws_hook_params=aws_hook_params,
        dag=dag
    )
    
    add_steps = EmrAddStepsOperator(
        task_id='add_steps',
        job_flow_id="{{ task_instance.xcom_pull(task_ids='create_emr_cluster', key='return_value') }}",
        aws_conn_id='aws_default',
        aws_hook_params=aws_hook_params,
        steps=SPARK_STEPS,
        dag=dag
    )
    
    step_checker = EmrStepSensor(
        task_id='watch_step',
        job_flow_id="{{ task_instance.xcom_pull('create_emr_cluster', key='return_value') }}",
        step_id="{{ task_instance.xcom_pull(task_ids='add_steps', key='return_value')[0] }}",
        aws_conn_id='aws_default',
        aws_hook_params=aws_hook_params,
        dag=dag
    )
    
    terminate_cluster = EmrTerminateJobFlowOperator(
        task_id='terminate_cluster',
        job_flow_id="{{ task_instance.xcom_pull(task_ids='create_emr_cluster', key='return_value') }}",
        aws_conn_id='aws_default',
        aws_hook_params=aws_hook_params,
        dag=dag
    )
    
    create_emr_cluster >> add_steps >> step_checker >> terminate_cluster