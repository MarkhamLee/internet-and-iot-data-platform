## CICD Pipeline Automation

--- Work in Progress: July 12, 2025---

Initial collection of code to enable CICD automation for things that are largely manual, e.g., redeploying climate monitoring containers on devices that aren't running on the K3s cluster.


#### Current Contents
* Script to restart a Docker container running on Portainer:
    * Restarts the container
    * Sends Slack alert with status of restart command, I.e., failure or success
* Checks for recent Docker Image update and calculates the age of it:
    * This meant for my private repos
* Docker image automate redeployment, leveraging the two items above:
    * Checks for the age of the latest image
    * If the image is older than an hour, it will:
        * Send an alert that a new image has been detected
        * Trigger a redeployment via the Portainer API
    * I built this to automate updates for simple containers I have running on Raspberry Pis for climate control, in addition some automations I'm building related to gardening. 
