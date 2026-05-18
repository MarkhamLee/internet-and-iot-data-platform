## Site Monitoring Agent --- WIP

### Origin Story

I'm a huge fan of a small Pennsylvania based company called "Mod House Audio" that makes bespoke hand made headphones, and also modifies (and dramatically improves) headphones from other manufacturers. The headphones are so coveted that the waiting list is usually several months out, finding a pair on the used market is rare and occasional b-stock units are often gone within 24-72 hours. While there are a variety of "page change" open source tools out there, I decided to build an LLM based one so the change detector could be context aware and flexible. I.e., something smart enough that it doesn't just detect a change, it can evaluate the change vs a set of criteria and determine if it's worth notifying me about.


### Initial Use Case

The initial use case involves tracking a b-stock page that typically contains custom orders for products with a large number of variants, and usually lists the subset of available items vs a page with a list of all items and an indicator as to whether the item is in stock. Additionally, there is a need to verify that the desired features and customizations are available. More specifically: there are three broad types of Mod House Audio Argons (MK2, MK3 and T60 MK1), which are built by modifying approximately 10 different Fostex RP model headphones. Context awareness helps not just properly detect what's available, but properly evaluate it vs what I'm looking for.


### Other Use Cases

While the initial use case is rare headphones, I can use this to monitor practically anything for context aware changes:
* **Software release notes:** a site monitoring alert can keep an eye out for specifically needed functionality or changes that could break the version I'm currently running in production.
* **Product release pages:** between the initial product announcement and the actual launch, product scope, name, features, etc., can change. With this monitoring agent I could write a set of criteria that is just looking for a product with a specific set of features. E.g., I don't need to know if FiiO releases a new digital audio player (DAP) with a specific name, I need to know if they release one that has these specific set of features.
* **Service Providers:** could monitor a local ISP and notify me when a) they now provide service where I live b) it's at at speed + price that makes it worthwhile to switch.


### How It Works 

I already have an Ollama instance running Qwen 3b available, so the "agent" just has to gather and prepare data, send it to the Ollama endpoint and then take actions based on what comes back. This centralized approach allows me to run several agents without having to spin load additional models and run additional ML capable compute.

It's a Docker based application that uses a Qwen 3b model running on Ollama (deployed to my K3s cluster) that runs as an Argo Workflow Cron job that periodically checks a page for specific content and uses an LLM to determine whether or not anything has changed. The web site address, and a prompt in terms of the desired state to look for are defined in a .yaml file. Based on the data in the config file the page is parsed and then sent to an LLM for evaluation.

#### Data Persisistence 
* Two tables in Postgres store relevant data:
    * Results from each check
    * An event table that stores things like a desired state being detected, or page going from a desired state (the thing is in stock) to an un-desired state (you moved too slow)

#### Minimizing LLM queries
* We use finger prints and hashes to minimize LLM queries:
    * Based on the prompt we track specific pieces of content to build a finger print and then we hash it.
    * The hashes are then stored in Postgres in the table for each page check
    * Subsequent page checks can use the hashes to determine if something related to the fingerprint has changes and if it's worth invoking the LLM
    * We also periodically re-check regardless of the hash change just in case the system missed something.

#### Notifications
* When a page change is detected we use Slack's block text feature to build and send a Slack message to alert me to the change.
* The system will periodically remind of the change as long as the desired state persists
* We use Typing + Pydantic to ensure that the data to and from Ollama is of the right shape



### Architecture (PENDING)




### Deployment & CI/CD 

* The agent runs as a Argo cron job that runs on a schedule 
    * The Argo workflow cron job manifest is pushed to Git where it's picked up by ArgoCD and applied to the cluster and the Argo Workflow controller picks up and manages it from there. 
    * The Argo UI is only used for monitoring workflows and diagnosing errors, all changes are made editing manifest files and then pushing the changes to Git.
* GitHub actions are used to build the Docker container and push it to Docker Hub. Changes will be used in the next run after the container is rebuilt.

