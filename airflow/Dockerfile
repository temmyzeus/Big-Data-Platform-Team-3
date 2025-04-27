ARG AIRFLOW_VERSION=2.10.5

FROM apache/airflow:${AIRFLOW_VERSION}

COPY --from=shared requirements.airflow.deps.txt /opt/airflow/

USER root

# System/OS Dependencies can be installed at this stage

USER airflow

# Python/Pip Dependencies can be installed here
RUN pip install --no-cache-dir \
    -r /opt/airflow/requirements.airflow.deps.txt

ENV PYTHONPATH=$AIRFLOW_HOME/etl:$PYTHONPATH
