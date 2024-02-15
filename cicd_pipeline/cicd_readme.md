## CICD Overview

Given the differences between deploying containers for ETL pipelines that run on a schedule and continuously running services, there will be an entry for each category's CI/CD pipeline as the approaches will be somewhat different. 


### ETL Pipelines

Nearly all ETL pipeline will be built as Docker containers so that they can be largely orchestration tool agnostic, meaning: the same container can be run via Airflow, Argo Workflows or even Kubernetes cron jobs without having to make changes to the container. This also makes CI/CD somewhat simple as all that's required is to automate the creation of container builds and push them to a container repository, in this particular case we use GitHub Actions & Dockerhub:

* Containers are built and tested locally, for more complex or new pipelines they may also be tested for a few days (or more) as Kubernetes cron jobs or via Airflow or Portainer in a beta environment. 
* Once testing is complete the code is pushed to Github, which will trigger a GitHub Action that will build a multi-architecture container (amd64, arm64) and push it to Docker Hub.
* The new container is then automatically picked by the ETL tool (Airflow or Argo Workflows) the next time the pipeline runs. 


### Continuously Services 

Currently testing a couple of approaches, the winning solution will likely leverage Argo CD and GitHub actions 



### Other Approaches 

Given this is a learning exercise, will also experiment with other CI/CD tools in the future, current items on the list include:
* GitLab
* Jenkins