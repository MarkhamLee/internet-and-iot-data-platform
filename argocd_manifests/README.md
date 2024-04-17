### Argo CD Manifests
Collection of manifests for managing apps with Argo CD. A couple off key details:
* Per best practices the Argo CD manifests/app configs are stored in a separate repo. I.e., separate your app code and app configs. Despite this, I have the Argo CD configs here just so that they're separate from the configs for the deployed apps, avoid accidentally synching the manifests and having duplicate deployments. This also allows me to tie the Argo configs to the specific project they support. 
* These can be either be applied at the command line with Kubectl or inserted into the Argo UI. 
