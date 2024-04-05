# Airflow Setup Files

This folder contains everything you'll need to get an Airflow instance up and running on a Kubernetes cluster, but with the caveat that I used this configuration on a local cluster and that when deploying into a cloud environment there will likely be some additional items you'll need to account for. That being said, the major building blocks are here so any changes you have to make "should" be small, but again Kubernetes + Airflow can be, tricky until it isn't. 

The "official" Airflow helm chart came with a values.yaml file that was well over 1000 lines AND included items that were deprecated, multiple methods to enter the same data, etc., SO I went with the Bitnami chart that was already available in Rancher, edited it and then deployed a basic Airflow instance from the command line, and then made tweaks and changes/iterated to get things how I wanted them. Once that was accomplished I downloaded the values.yaml file for future reference/use. 

You can find more details on the Bitnami Helm chart for Airflow [here](https://github.com/bitnami/charts/blob/main/bitnami/airflow/README.md)


#### Folder Contents
* fernet_key_generator.py to ensure your set up is properly secured/encrypted 
* values.yaml for use in deploying Airflow either from the command line or within a tool like Rancher 
* The Ingress file for accessing the web UI 
* pv.yaml and pvc.yaml are the persistent volume and persistent volume claim I created to ensure logs remaining once a pod was shutdown, make sure you apply pv.yaml and then pvc.yaml in order, i.e., create the persistent volume and then create the claim to it. 


## Deployment Steps

Before we begin, there are two main approaches and I strongly suggest the first if you haven't done this before: 

1) Just to start out with the default_values.yaml file (or deploy from Rancher) and get the basic setup working. I would suggest this approach as you'll at least have a known working configuration before you change anything. Also, if you change something and the deployment fails, your first step should be to roll back the deployment to the prior one that worked and then try again. Also, I would continously save known working values.yaml files, so you have a history of things that worked. 
2) Use my values.yaml file, but customized for your needs and/or environment. I'd suggest the first option, get something that deploys properly and then start changing settings. The items I changed (for the record) are:
    * Added Github data for logging into Github and synching with the repo that holds my dags:

    ```
    git:
    clone:
        args: []
        command: []
        extraEnvVars: []
        extraEnvVarsCM: ''
        extraEnvVarsSecret: '<name of your personal access token secret>'
        extraVolumeMounts: []
        resources: {}
    dags:
        enabled: true
        repositories:
        - branch: main
            name: repo_name
            path: /dags
            # Personal access tokens seem to work better with this helm chart (for me anyway)
            # Just go to your GitHub: settings --> Developer Settings --> Fine Grained Personal Access Tokens
            # name of the secret in the EnvVarsSecret and secret's key below 
            # Note: only necessary if you're synching a private repo and/or want to avoid "free account" rate limits
            repository: https://<your_github_username>:${key for your secret}@github.com/username/your_repo.git
    image:
        digest: ''
        pullPolicy: IfNotPresent
        pullSecrets:
        - dockersecrets # insert what you named your Docker secrets
        registry: docker.io
        repository: bitnami/git
        tag: 2.43.0-debian-11-r5
    plugins:
        enabled: false
        repositories:
        - branch: ''
            name: ''
            path: ''
            repository: ''
    sync:
        args: []
        command: []
        extraEnvVars: []
        extraEnvVarsCM: ''
        extraEnvVarsSecret: '<name of your personal access token secret>'
        extraVolumeMounts: []
        interval: 300
        resources: {}
    ```

* I also added my Docker creds so I can pull those images down: 

    ```
    image:
        digest: ''
        pullPolicy: IfNotPresent
        pullSecrets:
        - dockersecrets
        registry: docker.io
    ```

### Preparation Steps

1) Generate a fernet key via the python script, add that value to the values.yaml file
2) Create a config map with your python dependencies, using the command below:
```
sudo kubectl create -n airflow configmap requirements --from-file=requirements.txt
```
Once the above is complete, you'll need to update the values.yaml file in three separate places AKA the scheduler, web and worker sections:

~~~
  extraVolumeMounts:
    - mountPath: /bitnami/python/requirements.txt
      name: requirements
  extraVolumes:
    - configMap:
        name: requirements
      name: requirements
~~~

Managing python dependencies in Airflow is a royal pain, which is why I use the Kubernetes Pod operator so I can just deploy my tasks/dags/etls with Docker, and just maintain the dependencies in the container. E.g., if you're not using the pod operator and decide to update Python dependencies, you'll have to update the config map and then redeploy Airflow, whereas if you use the pod operator you can just update the requirements.txt file and rebuild the image.

3) Setup a GitHub repo with a basic DAG so you can test a) importing a DAG from a repo b) test the DAG and make sure it works. 

4) This set up revolves specifically around using the Kubernetes Pod Operator, so you'll need (obviously) to have a container registry setup, and containerized versions of your ETL scripts. 

5) Be familiar with creating Kubernetes secrets and config maps. 

### Suggested Approach
1) Get the initial setup deployed
2) Add the ingress, persistent volume and volume claim 
3) Set-up the Github synch and bring in some basic DAGs and just make sure everything works
4) Once the above is sorted, then move on to changing things like executors, adding extra python dependencies, etc. 


### Key Things to be Aware Of

1) If a prior deployment failed and re-deploy with new settings instead of rolling back, you might want to click into that component to get the pod view, scale it down to zero and then back up to, sometimes the changes won't "take" until you do that. 
2) When looking for hints and helps online, be sure they're using the same version of the Helm chart that you are. I.e., this is the Bitnami version, certain items are different on the chart from Airflow 
3) When I was importing things from Github, it only brought in DAGs not the custom external classes I had built to work with the DAGs. I ended up just using Docker containers for everything to avoid "dependencies hell" (among other reasons), so I didn't dig much into it, still, something to keep in mind. 
4) I'd deploy with the Celery Executor first, some of the others have additional dependencies that aren't immediately apparent from the instructions. I.e., get it working, running your pipelines or tasks and then experiment with different executors. 


References:
* Log persistence was the missing piece for my deployment, and I was able to figure that out via [Marc Lamberti's Airflow tutorial](https://marclamberti.com/blog/airflow-on-kubernetes-get-started-in-10-mins/). Note: he's deploying via the official Airflow helm chart, but these persistent volume setups worked just fine. 