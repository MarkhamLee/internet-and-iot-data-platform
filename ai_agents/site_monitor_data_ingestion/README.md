## Site Monitor – Content Ingestion

This folder contains the content ingestion component of the Site Monitor Agent. A broader overview of the full pipeline can be found in the [Site Monitor Agent README](../site_monitor_agent/README.md).

The site monitoring pipeline has two components:

* Content ingestion (this folder): retrieves data for each monitored site and uses hashes to determine whether a change has occurred that warrants evaluation by the research agent.

* Research agent: uses an LLM (Qwen 3.5 9B) to determine not just whether a site has changed, but whether the desired state change has occurred.

### What the ingestion pipeline does

For each site defined in the config file (provided as a Kubernetes ConfigMap), the ingestion pipeline:

1. Parses the page content for each monitored site.
2. Generates a fingerprint and hash of the relevant content for fast change detection.
3. Compares the current hash against the stored value to determine whether the site has changed.
4. Stores the result in Postgres for the research agent to consume.
5. Sends reminders for previously detected state changes that remain in the desired state.

The site monitoring content ingestion pipeline runs as a daily Argo Workflows cron job on the [K3s private cloud cluster](https://github.com/MarkhamLee/k3s-powered-private-cloud-homelab) that underpins this data platform. The cron job manifest is managed declaratively in Git and applied to the cluster via ArgoCD, where Argo Workflows picks it up via its CRDs.

### Setting up the Config File 

The example config file is setup specifically for use as a Kubernetes config map, however, if one where to run this as a stand-alone Docker container or from the command line, the content after "monitoring_targets.yml: |" is what you would use. Keep in mind that you'd need to un-indent things to the left. 

Key sections of the config file:
* **max_reminders** is for the maximum number of reminders you want to receive about a site change, values of 0 or there being no values or the max_reminders key not being in the file = you'll get site reminders until the site is no longer in a desired state. If you want to limit the number of reminders, you just need to use an integer value > 0. 
* **slack_channel** is based on the presumption that you would have a Slack webhook setup to receive alerts. 
* The **missed_it_message" is what goes out when the page is no longer in the desired state. 