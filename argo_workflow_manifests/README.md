## Argo Workflow Manifests

Contained in this folder are the example manifest files for deploying containerized ETL pipelines (see etl_pipelines folder) as pipelines/workflows on the Argo Workflow tool. I currently deploy these with ArgoCD, via just dropping the manifest in a folder in my IAC repo and then creating a project in ArgoCD that points to it. Once deployed in this fashion, the cron jobs, tasks, etc., will appear in the Argo UI.

If you don't use a tool like ArgoCD, these files can be applied to your Kubernetes cluster by applying them to your cluster with kubectl, the Argo UI or from the command line with the Argo CLI tool. However, I would still suggest using a tool like ArgoCD that allows you to maintain everything in Git, for the sake of version control, consistency, having a single source of truth, etc.

You'll notice that the manifests look very similar to the manifest you would use to deploy the same container as a cron job on Kubernetes save a few Argo specific changes, this is one of the key benefits of Argo Workflows IMO, as the learning curve is relatively mild if you're already familiar with Kubernetes. 

### Future Items
* DevOps & K3s automations: e.g., tasks that verify that certs are up to date, secondary monitoring of key resources for both K3s and my homelab in general. 
* Event driven IoT work flows and automations
* Build more agentic work flows 
