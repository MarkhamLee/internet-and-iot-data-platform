## CICD for 3rd Party Applications

3rd party applications are deployed in a fashion that is similar to the pattern for [custom code](cicd_for_custom_code.md):

### 3rd Party Apps on K3s

* Deployment manifests in an IAC repo are monitored by ArgoCD, these are usually an ArgoCD umbrella chart + a values.yaml file, with the former containing the source Helm chart and other deployment related data, and the values.yaml containing the specific to my cluster and use case configuration data. 
* In cases where a Helm chart isn't available or is difficult to work wtih, Kubernetes manifests are used for all the K8s resources needed to deploy the application. 
* Deployments are always pinned to a specific Docker container version, to ensure a redeployment doesn't accidentally introduce a breaking change


### 3rd Party Apps on Stand Alone servers
* These are deployed with Docker Compose files + Portainer 
* Similar to custom containers, the compose files are stored in private repo dedicated to IAC. 

More details on deploying 3rd party applications can be found in the repo for the [k3s cluster](https://github.com/MarkhamLee/k3s-powered-private-cloud-homelab) this platform runs on. 

