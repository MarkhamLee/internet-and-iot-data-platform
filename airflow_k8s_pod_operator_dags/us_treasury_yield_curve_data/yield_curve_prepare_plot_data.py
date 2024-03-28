# (C) Markham Lee
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Airflow DAG to run a container that that queries the Postgres table with the
# raw yield curve data, does some light transformations and then writes it to
# reporting table used for plotting the yield curve in Grafana.

from datetime import datetime
from kubernetes.client import models as k8s
from airflow import DAG
from airflow.providers.cncf.kubernetes.secret import Secret
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator  # noqa: E501

# define instance specific variables
env_variables = {"QUERY_FILE": "todays_curve.sql"}

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
    dag_id='yield_curve_plot_preparation',
    schedule='30 5 * * *',
    default_args=default_args,
    tags=['k8s-pod-operator-container', 'Python'],
    catchup=False,
) as dag:
    k = KubernetesPodOperator(
        namespace='airflow',
        container_resources=resource_limits,
        node_selector={'node_type': 'arm64_worker'},
        image_pull_secrets=[k8s.V1LocalObjectReference("dockersecrets")],
        image="markhamlee/yieldcurve_plot:latest",
        env_from=configmaps,
        env_vars=env_variables,
        labels=node_selector_labels,
        secrets=[secret_env1, secret_env2, secret_env3],
        cmds=["python3"],
        arguments=["main.py"],
        name="yield_curve_plot_data_pod",
        task_id="yield_curve_plot_data",
        is_delete_operator_pod=False,
        hostnetwork=False,
        get_logs=True,
        log_events_on_failure=True,
        in_cluster=True,
        startup_timeout_seconds=180
    )
