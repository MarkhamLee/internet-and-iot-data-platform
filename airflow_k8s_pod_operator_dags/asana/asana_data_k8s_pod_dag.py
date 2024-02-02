# (C) Markham Lee
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# DAG that ingests task data for a given project ID in Asana and then writes
# that data to Postgres, for monitoring from a centralized dashboard.
from datetime import datetime, timedelta
from kubernetes.client import models as k8s
from airflow import DAG
from airflow.kubernetes.secret import Secret
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator  # noqa: E501

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

secret_env4 = Secret(deploy_type="env", deploy_target="ASANA_KEY",
                     secret="asana-secret",
                     key="ASANA_KEY")

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 1, 24),
    'retries': 0
}

with DAG(
    dag_id='asana_tasks',
    schedule=timedelta(hours=1),
    default_args=default_args,
    catchup=False,
) as dag:
    k = KubernetesPodOperator(
        namespace='airflow',
        image_pull_secrets=[k8s.V1LocalObjectReference("dockersecrets")],
        image="markhamlee/asanadata",
        env_from=configmaps,
        secrets=[secret_env1, secret_env2, secret_env3, secret_env4],
        cmds=["python3"],
        arguments=["main.py"],
        name="asana_task_monitor_pod",
        task_id="asana_data_ingestion",
        is_delete_operator_pod=True,
        hostnetwork=False,
        get_logs=True,
        log_events_on_failure=True,
        in_cluster=True,
        startup_timeout_seconds=180
    )
