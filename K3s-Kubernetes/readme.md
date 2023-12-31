#### Short Overview

This folder contains the deployment files for various microservices I built to support the day to day running of this project, E.g. the Slack service was built specifically to be deployed on a K3s cluster to forward messages to Slack only from other services running on the same cluster. 

The folders for each custom micro-service are organized as follows:
* container - contains the Docker file and associated files to build the docker image for the container. 
* deployment_files: contains the files to deploy the container on Kubernetes as a service. 

I've also included deployment files for 3rd party applications that can be difficult to setup. Deployment files for the rest of the 3rd party apps can be [found in the repo I built](https://github.com/MarkhamLee/kubernetes-k3s-data-platform-IoT) for the Kubernetes cluster that this project runs on. 