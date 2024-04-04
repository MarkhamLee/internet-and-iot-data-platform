### Hardware Telemetry Containers & Scripts

Containerized python script(s) for retrieving telemetry data (temps, cpu load, RAM utilization, etc) from single board computers (SBCs) and other small devices deployed as edge devices, remote sensor stations or to support IoT applications. The general idea is that if a device is listed in this folder it's because I'm currently or plan to use it as an edge or IoT device, while in this repo's [companion project](https://github.com/MarkhamLee/kubernetes-k3s-data-and-IoT-platform) (for the Kubernetes cluster this one runs on) there is a similar folder but that holds monitoring code for devices that are primarily used as servers or Kubernetes nodes. 

In a few cases some devices can be used as servers or remote edge/IoT devices, rather than put code in both repos in those instances I'll just have a link. E.g., in the Raspberry Pi 4B folder in this repo, I just link to the Raspberry Pi monitoring folder in my Kubernetes repo. 
