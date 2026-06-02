## Dependabot Agent – Data Ingestion Pipeline

This folder contains the data ingestion pipeline for the Dependabot research agent. The agent researches security vulnerabilities in code dependencies surfaced by GitHub's Dependabot feature and suggests context aware remediations based on how each library is actually used in the codebase.

### Pipeline overview

The broader agent is split into two components:

* Data ingestion pipeline (this folder): pulls Dependabot alert data from the GitHub API for each monitored repository, transforms it into an LLM ready format, maintains alert state, and triggers Slack reminders for unresolved alerts.

* Research agent: consumes the prepared data from Postgres, evaluates each alert against the relevant codebase using Qwen 3.5, and writes back specific remediation recommendations.

Splitting ingestion from inference minimizes unnecessary compute. The data ingestion step runs in a fan out pattern: one container per monitored repository, and a single research agent instance handles the LLM calls across all repositories.

How the pipeline works:

1. Pulls open Dependabot alerts from the GitHub API for that repository.
2. For new alerts:
   - Transforms the raw alert data into an LLM ready payload.
   - Generates a fingerprint and hash of the alert for change detection.
   - Stores metadata such as first seen timestamp, affected subfolder or microservice, and dependency scope.
3. For existing alerts:
   - Compares hashes to detect whether an alert has changed in scope or severity.
   - Updates remediation status for alerts that have been resolved.
   - Sends Slack reminders for alerts that remain unresolved past the configured interval.

### Deployment and scheduling

The ingestion pipeline runs on an hourly schedule as an Argo Workflows cron job running on the [K3s cluster](https://github.com/MarkhamLee/k3s-powered-private-cloud-homelab) that underpins this data platform. Cron job manifests are managed declaratively in Git and applied to the cluster via ArgoCD.
