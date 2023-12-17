#### Short Overview

A collection of microservices I built specifically to support this project running on Kubernetes. E.g. the Slack service was built specifically to be deployed on a K3s cluster to forward messages to Slack only from other services running on the same cluster. The folders for each service are organized as follows:
* container - contains the Docker file and associated files to build the docker image for the container. 
* deployment_files: contains the files to deploy the container on Kubernetes as a service. 

