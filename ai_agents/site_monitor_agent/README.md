## Site Monitoring Agent --- WIP

### Origin Story

I'm a huge fan of a small company called Mod House Audio that makes bespoke hand made headphones, and also modies (and dramatically improves) headphones from other manufacturers. The headphones are so coveted that the waiting list is usually several months out, it's rare to find a pair used and while they do have b-stock sometimes, you have to act fast, as in 24-48 hours fast. While there are a variety of "page change" open source tools out there, I decided to build an LLM based one so the change detector could be context aware and flexible. I wanted a context aware change detector for collectible or other highly coveted items that needed to be smart enough to evaluate what's being offered, it's condition and if it's actually what I want. 


### Initial Use Case

The broad use involves tracking a b-stock page for which products are added and removed, and there are numerous variants within a product family. E.g., MK3 Argons can be built from Fostex T20RP, T50RP, T40RP and from Fostex collaboration products with other headphone related companies, however, regardless of the source material they're all rebuilt to be the same thing. Meaning: if on the 10th the page just shows Mod House's in hous headphones and say T40RP based MK3 Argons, and then the T40s are removed from the page and the next time Argons show up they're a T20RP variant, a regular change detector might not notice, nor could it summarize the condition the product is in, note any special features, etc. 


### Other Use Cases

While the initial use case is rare headphones, I can use this to monitor practically anything for context aware changes:
* Open source projects, instead of monitoring for a change to a release page, I can search for content related to specific features I want or regularly use. 
* 


### How It Works 

I already have an Ollama instance running tha Qwen 3b available, so the "agent" has to gather and prepare data, send it to Ollama endpoint and then take actions based on what comes back. This centralized approach allows me to run several agents without having to spin up additional compute. 

It's a Docker based application that uses a Qwen 3b model running on Ollama (deployed to my K3s cluster) that runs as an Argo Workflow Cron job that periodically checks a page for specific content and uses an LLM to determine whether or not anything has changed. 

* The web site address, and a prompt in terms of the desired state to look for are defined in a .yaml file. 
* Based on the data in the config file the page is parsed and then sent to an LLM for evaluation. 
* Two tables in Postgres store relevant data:
    * Results from each check 
    * An event table that stores things like a desired state being detected, or page going from a desired state (the thing is in stock) to an un-desired state (you moved too slow)
* We use finger prints and hashes to minimize LLM queries:
    * Based on the prompt we track specific pieces of content to build a finger print and then we hash it. 
    * The hashes are then stored in Postgres in the table for each page check 
    * Subsequent page checks can use the hashes to determine if something related to the fingerprint has changes and if it's worth invoking the LLM
    * We also periodically re-check regardless of the hash change just in case the system missed something. 
* When a page change is detected we use Slack's block text feature to build and send a Slack message to alert me to the change. 
* The system will periodcially remind of the change as long as the desired stat persists
* We use Typing + Pydantic to ensure that the data to and from Ollama is of the right shape  


### Architecture (PENDING)




### Deployment 

I have it deployed to as Argo Workflow cron job:
* The Argo workflow manifest is pushed to Git where it's picked up by ArgoCD and then applied to the cluster. 
* I mount the yaml config file as a config map in K3S
* Any changes that need to be made are made in GitHub where they're picked up within a few minutes by ArgoCD. 
* The agent is Docker based and GitHub actions are used to build new containers and push them to a private Dockerhub repo whenever code is pushed to Git

