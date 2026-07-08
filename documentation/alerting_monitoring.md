## Alerting, Monitoring & Notification

The current alerting and monitoring paths are: 

* **Slack Integration:** virtually all of the custom workloads running on this platform can send Slack messages for failures, state changes and other key events. For example:
    * The UPS monitoring containers will send Slack messages notifying that the power has gone out, next they will send regular updates around how long the UPS can run before the battery runs out, when power returns they will provide regular updates until the battery is recharged. 
    * ETLs send Slack messages if the pipeline fails, an external API isn't working, etc. 
    * Agentic workloads use Slack to send notifications for things like new dependabot security alerts, or when a web page is in the desired state. 
* **Custom Monitoring Containers:** custom monitoring for servers, UPS devices (via NUT), network devices, etc., that pushes telemetry data to InfluXDB, while also pushing data to services like Prometheus and Uptime Kuma to provide redundant monitoring and alerting. Grafana is used to monitor/view the data in InfluxDB. 
* **Prometheus Alert Manager:** can send alerts if a workload (task or continuously running) deployed to K3s fails to launch, crashes, etc. When the problem is fixed, Alert Manager will then send a "resolved" message. 
* **Prometheus:** the hardware monitoring containers have a "flag" for sending telemetry data to Prometheus/exposing a Prometheus target. This is used to monitor the state of external to K3s servers, e.g., Firwall, DNS servers, NAS servers, etc. 
* **Uptime Kuma:** hardware monitoring workloads can send "heartbeats" to Uptime Kuma, if a device isn't "heard from" within a certain period of time, Uptime Kuma can send a Slack notification that the device isn't available.
* **Victoria Logs:** workloads running on K3s have their logs collected via Victoria Logs.  

