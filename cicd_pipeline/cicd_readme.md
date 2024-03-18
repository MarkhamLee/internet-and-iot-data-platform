## CICD Overview

Given the differences between deploying containers for ETL pipelines that run on a schedule and continuously running services, there will be an entry for each category's CI/CD pipeline as the approaches will be somewhat different. 


### ETL Pipelines

Nearly all ETL pipelines are built as Docker containers so that they can be largely orchestration tool agnostic, meaning: the same container can be run via Airflow, Argo Workflows, Kubernetes cron jobs or any other tool that allows you to schedule/orchestrate containers without having to make changes to the container. This also makes CI/CD somewhat simple as all that's required is to automate the creation of container builds and push them to a container repository, in this particular case we use GitHub Actions & Docker Hub:

* Containers are built and tested locally, for more complex or new pipelines they may also be tested for a few days (or more) via Airflow, Kubernetes cron jobs or Portainer in a beta environment. 
* Once testing is complete the code is pushed to Github, which will trigger a GitHub Action that will build a multi-architecture image (amd64, arm64) and push it to Docker Hub. 
* The image build process is only triggered if the files used to build that particular image are updated.
* The new container(s) are then automatically picked by the ETL tool (Airflow or Argo Workflows) from Docker Hub the next time the pipeline runs. 


### Continuously Running Services 

* Unlike the ETL pipelines that build a new container each time the pipeline runs, continuously running services (E.g., monitoring air quality) only pull down an image/build a container when they're first deployed and won't rebuild the container unless a node fails, there is a configuration change, etc. I.e., there needs to be a mechanism to rebuild the container when a new image is available.
* Currently testing a couple of approaches, the winning solution will likely leverage Argo CD and GitHub actions to regularly check the repo for a new Docker image and then re-deploy all relevant services.


### Future items & Ideas

* Given this is a learning exercise, will also experiment with other CI/CD tools in the future, current items on the list include:
    * GitLab
    * Jenkins
* Need to look into making the containers more modular and/or build the capability to update several images at once. E.g., changing the base image for a Python based container due to a security issue requires manually editing several Dockerfiles, need to create the ability to make one update that the rest of the Dockerfiles inherit.