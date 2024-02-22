# (C) Markham Lee
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Python config file to run the Alpha Vantage T-Bill ETL container that pulls
# down daily T-Bill rates and writes them to PostgreSQL.
from datetime import datetime, timedelta
from kubernetes.client import models as k8s
from airflow import DAG
from airflow.providers.cncf.kubernetes.secret import Secret
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator  # noqa: E501

# define instance specific variables
env_variables = {"BOND_MATURITY": "2year",
                 "TBILL_TABLE": "two_year_tbill",
                 "COUNT": "7"}

resource_limits = k8s.V1ResourceRequirements(
            requests={
                'cpu': '400m',
                'memory': '256Mi'
                },
            limits={
                'cpu': '800m',
                'memory': '512Mi'
                },
            )

# load config maps from Kubernetes
configmaps = [
    k8s.V1EnvFromSource(config_map_ref=k8s.V1ConfigMapEnvSource(name="key-etl-variables"))]  # noqa: E501

# load all the required secrets from Kubernetes
secret_env1 = Secret(deploy_type="env", deploy_target="POSTGRES_USER",
                     secret="postgres-secrets", key="POSTGRES_USER")

secret_env2 = Secret(deploy_type="env", deploy_target="POSTGRES_PASSWORD",
                     secret="postgres-secrets", key="POSTGRES_PASSWORD")

secret_env3 = Secret(deploy_type="env", deploy_target="ALERT_WEBHOOK",
                     secret="slack-webhook-pipeline-failures",
                     key="WEBHOOK_ETL_ALERTS")

secret_env4 = Secret(deploy_type="env", deploy_target="ALPHA_KEY",
                     secret="alpha-vantage-secret",
                     key="ALPHA_VANTAGE_SECRET")

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 24),
    'retries': 0
}

with DAG(
    dag_id='alphavantage_2yr_tbill',
    schedule=timedelta(hours=12),
    default_args=default_args,
    catchup=False,
) as dag:
    k = KubernetesPodOperator(
        namespace='airflow',
        container_resources=resource_limits,
        node_selector={'etl_node': 'rpi4b'},
        image_pull_secrets=[k8s.V1LocalObjectReference("dockersecrets")],
        image="markhamlee/alphavantage_tbill_interval:latest",
        env_vars=env_variables,
        env_from=configmaps,
        secrets=[secret_env1, secret_env2, secret_env3, secret_env4],
        cmds=["python3"],
        arguments=["main.py"],
        name="alphavantage_2yr_tbill_pod",
        task_id="alpha_vantage_2yr_tbill",
        is_delete_operator_pod=True,
        hostnetwork=False,
        get_logs=True,
        log_events_on_failure=True,
        in_cluster=True,
        startup_timeout_seconds=180
    )
