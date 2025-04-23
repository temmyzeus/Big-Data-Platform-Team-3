from datetime import datetime, timedelta

import boto3
from airflow.models import Variable
from airflow.providers.amazon.aws.operators.emr import (
    EmrAddStepsOperator, EmrCreateJobFlowOperator, EmrTerminateJobFlowOperator)
from airflow.providers.amazon.aws.sensors.emr import EmrStepSensor

from airflow import DAG


def aws_session():
    session = boto3.Session(
                    aws_access_key_id=Variable.get('access_key'),
                    aws_secret_access_key=Variable.get('secret_key'),
                    region_name="us-east-1"
    )
    return session

JOB_FLOW_OVERRIDES: dict[str, Any] = {
    "Name": "PiCalc",
    "ReleaseLabel": "emr-7.1.0",
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
        ],
        # If the EMR steps complete too quickly the cluster will be torn down before the other system test
        # tasks have a chance to run (such as the modify cluster step, the addition of more EMR steps, etc).
        # Set KeepJobFlowAliveWhenNoSteps to False to avoid the cluster from being torn down prematurely.
        "KeepJobFlowAliveWhenNoSteps": True,
        "TerminationProtected": False,
    },
    "Steps": SPARK_STEPS,
    "JobFlowRole": "EMR_EC2_DefaultRole",
    "ServiceRole": "EMR_DefaultRole",
}



with DAG(
    dag_id="emr_orchestration",
    start_date=datetime(2024, 11, 22),
    schedule_interval='0 0 * * *',
    catchup=False
) as dag: