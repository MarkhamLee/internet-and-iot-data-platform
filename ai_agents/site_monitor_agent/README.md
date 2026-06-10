## Site Monitor – Research Agent

### Origin story

This agent started with a specific problem: [Mod House Audio](https://www.modhouseaudio.com/), a small Pennsylvania company that makes bespoke handcrafted headphones and dramatically improves headphones from other manufacturers, sells coveted b-stock units that typically sell out within 24–72 hours. Generic page-change tools weren't sufficient — the agent needed to be context-aware enough to evaluate not just whether a page changed, but whether the right change occurred.
Use cases

The same pattern applies broadly to anything that requires context-aware change detection rather than a simple diff:

* Rare or limited-availability products: monitor a b-stock or drop page for a specific configuration rather than any change.
* Software release notes: watch for functionality you need, or changes that could break a version currently running in production.
* Product announcement pages: track whether a product has shipped with the specific features you care about, not just whether the page updated.
* Service providers: monitor an ISP page for service availability and pricing at a specific location.

### Pipeline overview

The site monitoring pipeline has two components:

* Content ingestion: retrieves data for each monitored site, generates fingerprints and hashes for fast change detection, and flags sites that warrant LLM evaluation.

* Research agent (this folder): consumes flagged pages from Postgres and uses an LLM (Qwen 3.5 9B via Ollama) to determine whether the desired state change has occurred, then triggers notifications and updates state in Postgres.

Separating content ingestion from inference keeps compute usage efficient — lightweight ingestion containers run in parallel across all monitored sites, while a single agent container handles the LLM calls.

**How the research agent works** 

Target sites and their desired-state criteria are defined in a config file (provided as a Kubernetes ConfigMap). For each flagged site, the research agent:

1. Queries Postgres for pages flagged by the ingestion pipeline as changed.

2. Sends the page content and desired-state prompt to an Ollama instance running Qwen 3.5 9B for evaluation.

3. Writes the LLM's determination back to Postgres, updating the event table and result metadata.

4. Sends a Slack notification if the desired state is detected, and sends periodic reminders as long as that state persists.

**Minimizing LLM calls** 

The content ingestion pipeline handles hash-based filtering before the research agent is invoked, so the LLM is only called when content relevant to the desired-state fingerprint has changed. The pipeline also performs periodic full re-checks regardless of hash state to guard against missed changes.

**Data persistence** 

Two Postgres tables store agent state:

* Results table: one row per site check, recording the outcome and timestamp.
* Events table: records state transitions — desired state detected, or a page moving from desired back to undesired (e.g., an item going out of stock).

Pydantic models enforce the shape of data sent to and received from Ollama.

### Deployment

The research agent runs on a schedule as an Argo Workflows cron job on the [K3s private cloud cluster](https://github.com/MarkhamLee/k3s-powered-private-cloud-homelab) that underpins this data platform. Cron job manifests are managed declaratively in Git and applied to the cluster via ArgoCD. The Argo Workflows UI is used for monitoring and diagnosing runs only — all configuration changes go through Git.

Container images are built and pushed to Docker Hub via GitHub Actions. Updated images are picked up on the next scheduled run.