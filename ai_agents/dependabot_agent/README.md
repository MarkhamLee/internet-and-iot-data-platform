## GitHub Dependabot Research Agent

GitHub Dependabot is an automated service that scans repositories for dependencies with known security vulnerabilities and surfaces those alerts via email and the security tab on each repository. The Dependabot research agent takes this a step further by using an LLM to evaluate each alert in the context of the codebase it was found in:

- Security risk is expressed relative to how the vulnerable library is actually used, rather than as a generic severity rating.
- Breaking change risk is assessed proactively, with specific upgrade or refactor suggestions for the affected code.
- Remediation recommendations are tailored to the codebase rather than copied from generic CVE guidance.
    

## Pipeline overview

The broader agent is split into two components:

- **Data ingestion pipeline**: pulls Dependabot alert data from the GitHub API for each monitored repository, transforms it into an LLM-ready format, updates metadata for past alerts, and triggers Slack reminders for unresolved alerts.
- **Research agent (this folder)**: consumes prepared data from Postgres, evaluates each alert against the relevant codebase using Qwen 3.5, and writes back specific remediation recommendations.

Splitting the pipeline into separate ingestion and inference components keeps compute usage efficient: a single agent container handles the LLM calls while multiple lightweight ingestion containers run in parallel, one per monitored repository.

All components — Postgres, LLM inference, scheduling, and delivery — run on the [K3s private cloud cluster](https://github.com/MarkhamLee/k3s-powered-private-cloud-homelab) that underpins this data platform.

## Agent overview

On a nightly schedule, the research agent runs as an Argo Workflows cron job (Docker container) and performs the following steps:

1. Queries Postgres for alerts flagged as needing research — both newly ingested alerts and alerts older than the configured refresh threshold.
2. Sends each alert payload to an Ollama instance running Qwen 3.5 for evaluation.
3. Parses the LLM response and writes remediation recommendations back to Postgres, along with updated metadata recording when the alert was last researched.
4. Sends Slack notifications for new alerts and reminders for alerts that remain unresolved.