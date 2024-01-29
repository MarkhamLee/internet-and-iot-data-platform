### Argo Workflow Manifests

Contained in this folder are the manifest files for deploying containerized ETL pipelines (see etl_pipelines folder) as pipelines/workflows on the Argo Workflow tool. These files can be applied to your Kubernetes cluster either by using the Argo UI or from the command line with the Argo CLI tool. You'll notice that the manifests look very similar to the manifest you would use to deploy the same container as a cron job on Kubernetes save a few Argo specific changes, this is one of the key benefits of Argo Workflows IMO, as the learning curve is relatively mild if you're already familiar with Kubernetes. 

For the moment these are just "singular workflows" as far as all the logic and tracking is in the container, and these all run as a "1/1" in Argo. There is an option to set these up as DAGs with several steps, but doing that requires you to either use a separate container for each step and/or have separate scripts in the container that handle each step. 

Future Items:
* Add event driven workflows for the following:
    * CI/CD 
    * General management of the K3s cluster
    * The IoT side of this project, e.g., it would be relatively simple to add an event driven workflow that could do something like water a plant when the soil gets dry. 
