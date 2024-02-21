# (C) Markham Lee
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Python config file to run the Alpha Vantage T-Bill ETL container that pulls
# down daily T-Bill rates from the Alpha Vantage API and writes them to
# PostgreSQL.
from datetime import datetime, timedelta
from kubernetes.client import models as k8s
from airflow import DAG
from airflow.providers.cncf.kubernetes.secret import Secret
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator  # noqa: E501

# define instance specific variables
env_variables = {"BOND_MATURITY": "10year",
                 "TBILL_TABLE": "ten_year_tbill"}

resource_limits = k8s.V1ResourceRequirements(
            requests={
                'cpu': '200m',
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
    dag_id='alpha_vantage_10year_tbill',
    schedule=timedelta(hours=12),
    default_args=default_args,
    catchup=False,
) as dag:
    k = KubernetesPodOperator(
        namespace='airflow',
        container_limits=resource_limits,
        node_selector={'node_type': 'arm64_worker'},
        image_pull_secrets=[k8s.V1LocalObjectReference("dockersecrets")],
        image="markhamlee/alphavantagebondetl:latest",
        env_vars=env_variables,
        env_from=configmaps,
        secrets=[secret_env1, secret_env2, secret_env3, secret_env4],
        cmds=["python3"],
        arguments=["main.py"],
        name="alpha_vantage_10yr_tbill_pod",
        task_id="alpha_vantage_10yr_tbill_ingestion",
        is_delete_operator_pod=True,
        hostnetwork=False,
        get_logs=True,
        log_events_on_failure=True,
        in_cluster=True,
        startup_timeout_seconds=180
    )
