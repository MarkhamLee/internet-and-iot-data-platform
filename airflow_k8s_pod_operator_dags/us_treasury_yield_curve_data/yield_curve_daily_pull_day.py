# (C) Markham Lee
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Airflow DAG to run an ETL container that pulls downloads the latest yield
# curve data from the US Treasury

from datetime import datetime
from kubernetes.client import models as k8s
from airflow import DAG
from airflow.providers.cncf.kubernetes.secret import Secret
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator  # noqa: E501


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

node_selector_labels = {"kubernetes.io/arch": "arm64"}

# load all the required secrets from Kubernetes
secret_env1 = Secret(deploy_type="env", deploy_target="POSTGRES_USER",
                     secret="postgres-secrets", key="POSTGRES_USER")

secret_env2 = Secret(deploy_type="env", deploy_target="POSTGRES_PASSWORD",
                     secret="postgres-secrets", key="POSTGRES_PASSWORD")

secret_env3 = Secret(deploy_type="env", deploy_target="ALERT_WEBHOOK",
                     secret="slack-webhook-pipeline-failures",
                     key="WEBHOOK_ETL_ALERTS")

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 3, 27),
    'retries': 0
}

with DAG(
    dag_id='daily_yield_curve_data',
    schedule="0 5 * * *",
    default_args=default_args,
    tags=['k8s-pod-operator-container', 'Python'],
    catchup=False,
) as dag:
    k = KubernetesPodOperator(
        namespace='airflow',
        container_resources=resource_limits,
        node_selector={'node_type': 'arm64_worker'},
        image_pull_secrets=[k8s.V1LocalObjectReference("dockersecrets")],
        image="markhamlee/yieldcurve_daily:latest",
        env_from=configmaps,
        labels=node_selector_labels,
        secrets=[secret_env1, secret_env2, secret_env3],
        cmds=["python3"],
        arguments=["main.py"],
        name="daily_yield_curve_pod",
        task_id="daily_yield_curve",
        is_delete_operator_pod=False,
        hostnetwork=False,
        get_logs=True,
        log_events_on_failure=True,
        in_cluster=True,
        startup_timeout_seconds=180
    )
