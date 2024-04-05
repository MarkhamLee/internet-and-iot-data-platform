## K3s Deloyment Files for the Slack Alert Service

Use the slack_service_values.yaml file to deploy the slack service container on Kubernetes. Prior to using it there are a couple of preparatory steps that need to be taken care of first:
* Create a namespace and store the secrets for your Slack account AND your Docker Repo 
* Create the image in the container folder and push it to the repo where you store your Docker images 
* Update the values file for your specifc cluster, service names, namepaces, etc. 

Once the preparations are finished you just need to apply it from the command line either on one of the server nodes of your cluster OR via a machine with remote access to it. Namely, run the following command:

```sudo kubectl apply -f slack_service_values.yaml```

Provided there are no errors in the YAML files, which will be typically be things like service names, docker image repos, etc., the service should deploy just fine and be up and running in a minute or two. 

There is an ingress file included as well if you wanted to make these endpoints available outside of the cluster, please make note that you have to have an entry in the ingress file for each endpoint. 

