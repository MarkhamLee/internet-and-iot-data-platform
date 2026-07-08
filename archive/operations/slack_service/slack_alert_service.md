## Slack Alert Service

I created this so I could send alerts via Slack by just pinging an endpoint rather than having to include code for the Slack client, et al, in each individual service I wanted to send alerts from. The implementation is fairly simple, it's just a Flask & Gunicorn wrapper around a simple Slack API client. The secret for the send_message endpoint is stored within Kubernetes and retrieved by the service, which further reduces complexity as I don't have to copy/clone the Slack secrets into multiple namespaces for each service.

Using the various endpoints is fairly easy:
    * /send_message: you just use a post request that includes the message, and slack channel for the send_message endpoint
    * /send_message_webhook: web hook + a message 
    * /ping just lets you know the service is running properly by responding with 'ok' 

I "might" update things in the future to just put the key name in the API request so I can use the service with multiple Slack accounts, but the current implementation serves my purposes just fine. 