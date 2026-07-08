## ETL Archive

These are ETLs that are no longer in use because they got replaced with something written in a different language, rolled into another service (e.g., [GitHub Dependabot agent](../../ai_agents/dependabot_agent/README.md)), etc., or are just no longer in use. Putting them here in an archive folder in case they're useful in the future. 

### Current Contents

* [Raspberry Pi Locator](rpi_locator/README.md) I built this during the Pi shortage of the early 2020s when you had to move fast to get a Pi at a decent price or get one at all. I haven't run this in a few years and with the [Pi Locator site shutting down](https://hackaday.com/2026/06/24/raspberry-pi-locator-website-to-shut-down-in-july/), there isn't much use for it anymore. All that being said, it's a good example of using Python to consume an RSS feed. 

* [GitHub Dependabot](github_dependabot) - a simple GitHub dependabot ETL that ingested GitHub dependabot data and counted the issues for a basic Dashboard that displayed how many open security issues there were. It was later replaced by a version that wrote detailed data for each alert to Postgres, for later analysis by an LLM. 

* [GitHub Dependabot V2](github_dependabot_v2) - this variant wrote detailed data on each GitHub dependabot alert to Postgres for later analysis by an LLM. An updated variant of this one is available [here](../../ai_agents/dependabot_data_ingestion/README.md), it was moved to the ai_agents folder so that all the components for the Agentic pipelines were in one place. 