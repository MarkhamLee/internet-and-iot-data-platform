## Agentic Workflows

This folder contains "AI Agents" autonomous workflows that enhance the "traditional" data ingestion and automation capabilities of the various pipelines and services in this repo. Meaning: these aren't pure "agentic workflows" where everything is done by an LLM, instead agents are integrated in what would normally be deterministic or traditional workflows in order to expand their capabilities. 

 A traditional ELT workflow around GitHub Dependabot alerts would consume the data from the GitHub API and then have logic around surfacing alerts and reminders. An AI enhanced version can doesn't just surface a generalized "medium severity alert" for a given library, it instead evaluates the alert's severity vs how the library is being used, can generate customized refactoring suggestions and can proactively identify risk related to breaking changes. E.g., the agent could identify an instance where a medium severity alert is actually a high severity one given how the library in question is used, while also noting that bumping version could cause breaking changes so a refactor makes more sense. 


### General Architecture 

![Agentic Architecture](/images/agentic_architecture_v1.png)  

#### Key Features:
* A CI/CD pipeline using GitHub Actions, Docker Hub and ArgoCD to build container images, maintain manifests and then apply them to the cluster for the run time tools to pick up. Everything is managed in Git. 
* Argo Workflow is the orchestration engine, running all scheduled and event driven agent tasks
* LLM Inference: Ollama (secured by Traefik, Technitium and an OPNsense firewall) serving Qwen models, behind an endpoint only accessible from within the K3s cluster.
* Observability and alerting is handled by Prometheus, Slack and Victoria log, with additional instrumentation and inference latency stats stored in Postgres. Grafana is used to visualize and analyze the data. 

### Agent Job Specifics

The typical agent is comprised of two more more Dockerized pipelines, i.e., the "Agent Job Container" is a broad term encompassing two or more pipelines: 
1) **Data Ingestion Pipeline:** brings in and transforms raw data into an LLM ready data payload, adds metadata, tracks status of prior data (e.g., a security alert) and then writes the data to Postgres 
2) **Agentic Pipeline:** consumes the "LLM ready data" from Postgres, makes the LLM calls and then takes actions inclusive of sending alerts, adding additional metadata to the original payload, etc. 


### Current Agents 
* Dependabot alerts: enriching the GitHub dependabot code library security alerts, so that they're less generalized and more specific to the "how and what" around how the code library is being used. 
* Intelligent Site Monitoring: granular site monitoring/change detection, by providing natural language instructions you can beyond "site changed updates" to monitoring the page for specific content rather than it simply changing. 


### Future Items
* Extend capabilities of the Dependabot agent to not just research security alerts for NPM libraries, but to research and suggest package.json files that can be dropped into a service's dependencies without causing breaking changes. 