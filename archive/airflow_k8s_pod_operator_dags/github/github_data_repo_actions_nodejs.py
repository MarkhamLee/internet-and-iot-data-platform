# (C) Markham Lee
# https://github.com/MarkhamLee/productivity-music-stocks-weather-IoT-dashboard
# Airflow DAG to pull down and run an ETL container that connects to the GitHub
# API, pulls down data related to Actions: minutes used, remaining, etc., and
# then writes that data to InfluxDB.
from datetime import datetime, timedelta
from kubernetes.client import models as k8s
from airflow import DAG
from airflow.providers.cncf.kubernetes.secret import Secret
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator  # noqa: E501

# define instance specific variables
env_variables = {"GITHUB_DATAPLATFORM_ACTIONS_MEASUREMENT": "data_dashboard_actions",  # noqa: E501
                 "REPO_NAME": "finance-productivity-iot-informational-weather-dashboard/"}  # noqa: E501

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


# load config maps from Kubernetes
configmaps = [
    k8s.V1EnvFromSource(config_map_ref=k8s.V1ConfigMapEnvSource(name="key-etl-variables"))  # noqa: E501
]

# load all the required secrets from Kubernetes
secret_env1 = Secret(deploy_type="env", deploy_target="GITHUB_TOKEN",
                     secret="github-api-token", key="GITHUB_TOKEN")

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
    dag_id='github_actions_data_dashboard',
    schedule=timedelta(minutes=60),
    default_args=default_args,
    catchup=False,
    tags=['k8s-pod-operator-container', 'Nodejs - TypeScript'],
) as dag:
    k = KubernetesPodOperator(
        namespace='airflow',
        container_resources=resource_limits,
        node_selector={'node_type': 'arm64_worker'},
        image_pull_secrets=[k8s.V1LocalObjectReference("dockersecrets")],
        image="markhamlee/github_repo_actions_nodejs",
        env_vars=env_variables,
        env_from=configmaps,
        secrets=[secret_env1, secret_env2, secret_env3],
        name="github_actions_data_dashboard_pod",
        task_id="github_actions_data_dashboard",
        is_delete_operator_pod=True,
        hostnetwork=False,
        get_logs=True,
        log_events_on_failure=True,
        in_cluster=True,
        startup_timeout_seconds=180
    )
