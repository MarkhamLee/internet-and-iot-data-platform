## Network Management

Custom code, scripts and the like to facilitate network automation, monitoring, et, al. 

### Current Contents

#### Tailscale Monitoring: 

Periodically checks the Tailscale API and verifies that a an exit node is available and gets the connection latency with a given city, and the writes the data to InfluxDB. If the node's last seen time was less than a minute ago, it will send a Slack alert that the device is offline. I'm still investigating the Tailscale API but for now I'll use this monitoring, with future plans to automate switching to an available exit node and/or one with better connectivity. 


### Future Plans
* Automate more around managing a tailnet
* Explore the pfSense API
* Running POCs on a variety of network security tools, will likely build some custom items for those as well


