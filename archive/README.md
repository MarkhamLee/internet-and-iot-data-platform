## Archived Content

Placing items in this folder that are no longer used, but "could" be used or referred to later. 

### Current Contents 

* **Airflow:** this project originally started as a way to learn Airflow, but when the project shifted into someting I just use/need regularly, I switched to using Argo Workflow, as it was easier to manage both from deploying new tasks and day to day maintenance of the task orchestration platform. The archive content for Airflow falls into two categories: 
    * [Airflow_k8s_pod_operator_dags](airflow_k8s_pod_operator_dags) - these are more config file "DAGs" (or Airflow specific Kubernetes manifests) that were used to spin up task containers and deploy them as pods on K8s. This is [my preferred approach](airflow_k8s_pod_operator_dags/README.md) to using Airflow.
    * [Airflow Python Dags](airflow_python_dags) - theser are the typical DAGs you deploy within Airflow, however, they're very specific to Airflow and won't work outside of it. 

* [ETL Archive](etl_archive/README.md) - this is a collection of deprecated ETL containers/code that is no longer being used, due to being wholly replaced by an ETL in different language, being folded into a different workflow or because it's no longer in active use. 