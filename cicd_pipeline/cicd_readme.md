## CICD Overview

Given the differences between deploying containers for ETL pipelines that run on a schedule and continuously running services, there will be an entry for each category's CI/CD pipeline as the approaches will be somewhat different. 


### ETL Pipelines

Nearly all ETL pipelines are built as Docker containers so that they can be largely orchestration tool agnostic, meaning: the same container can be run via Airflow, Argo Workflows, Kubernetes cron jobs or any other tool that allows you to schedule/orchestrate containers without having to make changes to the container. This also makes CI/CD somewhat simple as all that's required is to automate the creation of container builds and push them to a container repository, in this particular case we use GitHub Actions & Docker Hub:

* Containers are built and tested locally, for more complex or new pipelines they may also be tested for a few days (or more) as Kubernetes cron jobs or via Airflow or Portainer in a beta environment. 
* Once testing is complete the code is pushed to Github, which will trigger a GitHub Action that will build a multi-architecture image (amd64, arm64) and push it to Docker Hub. 
* The image build process is only triggered if the files used to build that particular image are updated.
* The new container(s) are then automatically picked by the ETL tool (Airflow or Argo Workflows) from Docker Hub the next time the pipeline runs. 


### Continuously Running Services 

* Currently testing a couple of approaches, the winning solution will likely leverage Argo CD and GitHub actions. The key feature is that unlike ETL pipelines that are regularly building containers on a schedule and checking for new images, the continuously running containers/micro-services need an external trigger to *redeploy themselves* whenever a container is updated.  


### Future items & Ideas

* Given this is a learning exercise, will also experiment with other CI/CD tools in the future, current items on the list include:
    * GitLab
    * Jenkins
* Need to build out some core/base images the other images can leverage. E.g., if I update the python baseline image, I can just update it once and then the other images will pick it up, as opposed to having to go into each Dockerfile and update the Python base. 