## CICD for Docker containers

### Build Process
Container builds are fully automated via GitHub Actions, pushing new code to GitHub triggers an image build that is then pushed to Docker Hub, but could also (if needed) be pushed to other container registries. Each container is built using a two stage build process to minimize the size of the image and reduce the security risk surface area. 

![Primary CI/CD Pipeline](../images/container_cicd.png)
 *Note: after fine tuning this approach for this project, I then used it on production/work projects as well, just with the containers landing in AWS ECR instead of Docker Hub*

### Deployment
* For constantly running containers, e.g., monitoring UPS devices, the updated container is redeployed via ArgoCD. 
* For job, etl or task based containers that run on a schedule on K3s via Argo Workflows:
    * The cron job is "loaded" into Argo Workflows via a cron job manifest (specific to Argo Workflows) that is stored in a GitHub repo for IAC that is being monitored by ArgoCD. When a manifest is changed or added, ArgoCD will pick those changes up and apply them to the K3s cluster for Argo Workflows to use. 
    * These tasks are nearly always deployed using the "latest" image tag so that the next time the job runs the most up to date version of the container is used. In instances where cron job manifest is pinned to a specific image version, the cron manifest will have to be updated and then pushed to GitHub so that ArgoCD can push those changes to Argo Workflows.

### Versioning
Semantic versioning is handled by a "VERSION" file in the folder containing the code for each container, updating a container's code also requires incrementing the version file so that the build process has the updated container version. Semantic versioning provides the following benefits:

* The most obvious is being able to roll back to an earlier service version if the latest version causes breaking changes 
* The use of shared components means that sometimes breaking changes can be introduced that will require updates across several ETLs, IoT tasks, etc., pinning to a specific version means we can prevent breaking changes from being introduced to a task or job until it's code has been updated. 

![Versioning Example](../images/container_versioning.png)

A repo wide GitHub action scans all the VERSION files and produces a [registry file](../container_versions_generated.yaml) listing all the containers in the registry that are built using semantic versioning. 

![Repo Container Registry](../images/container_registry.png)


### Container Architecture(s) 

* Custom containers that are targeted exclusively for deployment on K3s are built for x86 architecture only 
* Containers that could be deployed to K3s or to stand-alone devices (e.g., IoT Monitoring related) are built to run on ARM and x86 architectures. 


### Additional Details

* The containers are built using shared or private library components for common tasks, which means that if a shared component is updated, all the containers that use it will automatically be rebuilt, thus ensuring that they can use the updated shared resources. The versioning approach is used to prevent breaking changes from updated shared components from breaking currently running containers or jobs.