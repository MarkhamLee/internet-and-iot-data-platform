## ETL Containers & Scripts

Once I decided to start experimenting with different Airflow executors and other tools to build ETL pipelines, I decided to rebuild all of my ETL pipelines (originally as Airflow DAGs) into containers for a couple of reasons: 

1) While I really like Airflow its DAG format isn't very portable and they can be difficult to test locally, by moving to containers not only are my pipelines easier to test but they're now portable and can be used with a variety of different tools. 

2) Continuing from point #1... most ETL tools are really just orchestrators and schedulers, good engineering practice (especiallty for data engineering) is to ensure that things are as portable and shareable as possible. I.e. once you have a working container, deploying it on Airflow vs Argo Worflow vs OpenFaaS vs Kubernetes Cron Jobs is relatively easy, as you just need to edit what's usually no more than 1-2 dozen lines of a config or deployment file. 

This folder holds fully operational ETL containers, however, you'll need to acquire the API keys, setup the appropriate databases, populate environmental variables and configure a Slack webhook to receive pipeline failure alerts in order to use them. 

### Deployment Notes

* The folder for each pipeline/data source will have a readme file that will list all the environmental variables you'll need to run the container. Meaning: API keys for data sources, secrets for databases, and other pieces of data you'll need for the pipeline to work.

* For the Slack alerts you'll need to sign-up for the [Slack API](https://api.slack.com/), create a channel for receiving pipeline alerts and a web hook to send alerts to that channel.

* I use the Loki Stack for aggregating/consuming logs, and configured all the containers to write logs to stdout so they can be picked up by Loki via Promtail 

* I stored all secrets in Kubernetes and stored all other env variables in Kubernetes config maps 


### Docker Build Notes

A lot of these ETL processes use a lot of common code for writing to DBs, logging, pinging different endpoints from the same API provider, etc., so I've written the Dockerfiles to pull those scripts from common folders (see: "etl_library" and "openweather_library"). My plan is to use this approach as the basis for CI/CD pipelines that can build images and deploy containers, without a lot of manual steps. 

Keep in mind that building Docker images from different folders like this (namely from the parent folder the Docker file is in), is slightly tricky because when using the standard Docker build command, the Dockerfile can't copy files from the parent folder for security reasons. SO, to build the images you'll need to run a command like the following from the etl_pipelines folder so the parent folder is the "Docker build context": 

~~~
docker build -t openweather_airquality:latest -f openweather_air_quality/Dockerfile .
~~~

This command will set the parent folder with the common libraries as the "Docker build context", which will allow you to copy all the required files into your image. 

### Testing 
* The testing process was:
    * Just running the python scripts locally
    * Building the images and then running them as K8s cron jobs and/or via Portainer

Once the above was fine, I would then deploy them with one or more orchestration tools. 

