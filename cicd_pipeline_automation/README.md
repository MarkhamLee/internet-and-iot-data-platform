## CICD Pipeline Automation

--- Work in Progress: July 12, 2025---

Initial collection of code to enable CICD automation for things that are largely manual, e.g., redeploying climate monitoring containers on devices that aren't running on the K3s cluster.


#### Current Contents
* Script to restart a Docker container running on Portainer:
    * Restarts the container
    * Sends Slack alert with status of restart command, I.e., failure or success


