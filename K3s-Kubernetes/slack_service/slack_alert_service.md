## Slack Alert Service

I created this so I could send alerts via Slack by just pinging an endpoint rather than having to include a code for the Slack client, et al, in each invidivudal service I wanted to send alerts from. Using the various endpoints is fairly easy:
    * /send_message: you just use a post request that includes the message, and slack channel for the send_message endpoint
    * /send_message_webhook: web hook + a message 
    * /ping just lets you know the service is running properly by responding with 'ok' 

The secret for the send_message endpoint is stored within Kubernetes and retrieved by the service, which further reduces complexity as I don't have to copy/clone the Slack secrets into multiple namespaces. 