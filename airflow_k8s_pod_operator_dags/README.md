## Airflow DAGS for use with Kubernetes Pod Operator

### What's Here

The DAGs in this folder differ from typical Python DAGs in that there isn't any ETL logic in them, instead they're configuration files are used to spin-up/manage Docker containers that contain all the ETL logic, run all the tasks, etc., using the Kubernetes Pod Operator. The [Kubernetes Pod Operator](https://airflow.apache.org/docs/apache-airflow-providers-cncf-kubernetes/stable/operators.html) enables each DAG to run as a container on its own pod within Kubernetes. The basic mechanic is that you write a configuration file in Python or YAML that Airflow then uses to spin-up the container with your ETL logic/code. Once the container is completed the logs are exported and the pod is deleted. 

#### This approach offers several advantages: 

* **Simpler, Portable ETL Pipelines:** the same container can be run via Airflow, Argo Workflow, Kubernetes Cron jobs and other orchestration tools with zero modifications to the pipeline container. Deployment is as simple as creating the config file or manifest for the respective tool, and you can often re-use prior ones as you rarely have to change more than a dozen lines of Python or YAML.
* **Professional Development & a Proven Strategy:** I've read quite a few technical blogs from companies with very complex data engineering needs that have taken this strategy, so not only is it a proven approach but its one that I be focusing my skills development on. 
* To avoid issues related to Python dependencies, there are multiple ways to add python dependencies to support your DAGs: bake them into Airflow's docker container or add them as config maps, but those methods require you to re-deploy Airflow AND you can only have one version of a dependency at a time. Moving everything to a the K8s pod operator allows me to avoid this issue.
* Finally, it removes the dependency on Python created by using "traditional DAGs", in that I can now write ETL pipelines in virtually any language I can run in a Docker container.


### How to use/deploy
* The code for the ETL containers is in the etl_pipelines folder, just grab any code you want to re-use and then select the respective DAG from this folder. 
* Build the container from the above and upload it to the repository of your choice
* Configure the DAG and your K8s instance with the required environmental variables and secrets
* If you help with setting up Airflow, details on my setup are available [here](https://github.com/MarkhamLee/kubernetes-k3s-data-platform-IoT)