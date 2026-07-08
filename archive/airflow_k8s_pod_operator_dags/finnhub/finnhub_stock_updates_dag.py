# (C) Markham Lee 2023 - 2024
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Airflow DAG to run an ETL container that pulls data from the Finnhub stock
# data API and then writes that data to InfluxDB. This DAG is basically a
# pythonic configuration file, which is used to load and run the ETL that does
# the actual ETL work.
from datetime import datetime, timedelta
from kubernetes.client import models as k8s
from airflow import DAG
from airflow.providers.cncf.kubernetes.secret import Secret
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator  # noqa: E501


# define instance specific variables
env_variables = {"STOCK_SYMBOL": "SPY"}

# load config maps from Kubernetes
configmaps = [
    k8s.V1EnvFromSource(config_map_ref=k8s.V1ConfigMapEnvSource(name="key-etl-variables"))  # noqa: E501
]

resource_limits = k8s.V1ResourceRequirements(
            requests={
                'cpu': '200m',
                'memory': '128Mi'
                },
            limits={
                'cpu': '400m',
                'memory': '256Mi'
                },
            )

# load all the required secrets from Kubernetes
secret_env1 = Secret(deploy_type="env", deploy_target="FINNHUB_SECRET",
                     secret="finnhub-secret-key", key="FINNHUB_SECRET")

secret_env2 = Secret(deploy_type="env", deploy_target="INFLUX_KEY",
                     secret="influxdb-secret", key="PROD_INFLUX_KEY")

secret_env3 = Secret(deploy_type="env", deploy_target="ALERT_WEBHOOK",
                     secret="slack-webhook-pipeline-failures",
                     key="WEBHOOK_ETL_ALERTS")

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 24),
    'retries': 0
}

with DAG(
    dag_id='finnhub_stock_etl_spy',
    schedule=timedelta(minutes=15),
    default_args=default_args,
    catchup=False,
) as dag:
    k = KubernetesPodOperator(
        namespace='airflow',
        container_limits=resource_limits,
        node_selector={'etl_node': 'rpi4b'},
        image_pull_secrets=[k8s.V1LocalObjectReference("dockersecrets")],
        image="markhamlee/finnhub_stock_etl:latest",
        env_vars=env_variables,
        env_from=configmaps,
        secrets=[secret_env1, secret_env2, secret_env3],
        cmds=["python3"],
        arguments=["main.py"],
        name="finnhub_stock_price_pod_spy",
        task_id="finnhub_spy",
        is_delete_operator_pod=True,
        hostnetwork=False,
        get_logs=True,
        log_events_on_failure=True,
        in_cluster=True,
        startup_timeout_seconds=180
    )
