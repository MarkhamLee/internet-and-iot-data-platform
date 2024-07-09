## ETL Containers & Scripts

**Airflow is the primary tool for managing ETLs**, however, since all ETLs are containerized, they can easily be run with other tools like **Argo Workflow**, **Kubernetes cron jobs,** or any other tool that allows you to schedule containerized workloads. 
![ETL Workflow](images/airflow.png)  


### Typical End-to-End ETL Workflow
![ETL Workflow](images/ETL_workflow_v1.1.png)  

All the ETL pipelines have been built as Docker containers for a couple of reasons:

All the ETL pipelines have been built as Docker containers for a couple of reasons: 

While I really like Airflow and find that its DAG format is an excellent way to build and manage ETL pipelines, the fact remains that DAGs are difficult to test outside of Airflow and are not very portable. Containerizing all the ETLs ensures that the pipelines are easier to test and makes them tool agnostic since most of the tools one would use to manage ETL pipelines, are at their score, schedulers, and task management tools. 

I.e., once you have a working container, deploying it on Airflow vs Argo Workflow vs Kubernetes Cron Jobs is easy as you just need to edit what is typically no more than a couple dozen lines of a configuration file.  

This folder holds fully operational ETL containers, however, you will need to acquire the API keys, setup the appropriate databases, populate environmental variables and configure a Slack webhook to receive pipeline failure alerts to use them. In keeping with the "Dockerized ETL" theme: while most of the pipelines are written in Python, I have added Node.js variants for several of them, which you can find them [here](https://github.com/MarkhamLee/finance-productivity-iot-informational-weather-dashboard/tree/main/etl_pipelines_nodejs); I also plan to add some Scala versions in the near future. 

### CI/CD & Docker Build Notes

GitHub Actions is used for CI/CD automation, pushing updated files for an ETL pipeline to GitHub will trigger the rebuilding of its Docker image and then push it to Docker Hub, where it will be pulled down/used the next time the ETL pipeline runs. Each image is built for amd64 and arm64 architectures so it can be used by both architecture types in my Kubernetes cluster. *Note: currently, I am only running these workloads on my arm64 devices, as its more energy efficient* 

Nearly all of the ETL pipelines use common python scripts/private libraries for writing to DBs, logging, pulling data from certain providers, etc., so I've written the Dockerfiles to pull those scripts from common folders (E.g., "etl_library" and "openweather_library"). Used in conjunction with the CI/CD approach, this means that updating (for example) the script that writes to Postgres results in every image that uses that script being rebuilt when that code is pushed to GitHub. 

### Testing 
* The testing process is:
    * Use a unit testing library for the respective language (E.g. Jest for Node.js, Unittest for Python) to test the end-to-end ETL, plus ensure that exception handling and alert triggers are working properly. 

    * Once the above was complete the updates would be pushed to GitHub, this would trigger the automated build process for the Docker images, from there the images would often be tested further via Portainer and/or K8s cron jobs before deploying them via Airflow or Argo Workflow. 

### Future Plans

* Add Scala based ETLs 
* Add Spark (Python and Scala variants) based ETLs
* Experiment with splitting up the ETLs further into component containers, e.g., the main ETL container pulls data from an API and then passes that on to a generic container for writing to InfluxDB. This would allow me to build a single pipeline that uses multiple languages, helpful in instances where a particular language has simpler or better libraries for executing a particular task. 

### Building Images Manually 

Keep in mind that building Docker images from different folders like this from the CLI (namely from the parent folder the Docker file is in), is slightly tricky because when using the standard Docker build command, the Dockerfile cannot copy files from the parent folder for security reasons. SO, to build the images you will need to run the build command from the etl_pipelines folder so the parent folder is the "Docker build context": 

~~~
docker build -t openweather_airquality:latest -f openweather_air_quality/Dockerfile .
~~~

This command will set the parent folder with the common libraries as the "Docker build context", which will allow you to copy all the required files into your image.  

You can also build the multi-arch containers from the command line as well, as before this command needs to be run from the "etl_library" folder and you need to provide the path to the Dockerfile you want to use:  

~~~
docker buildx build --push  --platform linux/arm64/v8,linux/amd64 --tag  markhamlee/openweather_current:latest --file openweather_current/Dockerfile .
~~~

This command would build linux containers for arm64 and amd64 architectures, modify it for building for other architectures as you see fit.

###   Deployment Notes

* The folder for each pipeline/data source will have a readme file that will list all the environmental variables you will need to run the container. Meaning: API keys for data sources, secrets for databases, and other pieces of data you will need for the pipeline to work. 

* For the Slack alerts you will need to sign-up for the [Slack API](https://api.slack.com/), create a channel for receiving pipeline alerts and a web hook to send alerts to that channel.

* I use the Loki Stack for aggregating/consuming logs, and configured all the containers to write logs to stdout so they can be picked up by Loki via Promtail.

* I stored all secrets in Kubernetes and stored all other env variables in Kubernetes config maps.
