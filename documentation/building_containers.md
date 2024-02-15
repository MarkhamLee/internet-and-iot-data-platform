## Notes on building containers 

* Containers are built to be multi-architecture for amd64 and arm64 so they can run on either of the types of devices I have in my Kubernetes cluster, without my having to run two separate build processes, maintain different Dockerfiles, etc. 
* To build the multi-arch containers you'll need to use Docker buildX, which should be installed on your system if you've installed Docker Desktop. 
* The multi-arch command is below, it will build an image with one tag, but with a variant for each architecture and push up to Dockerhub all in one go. 

```
docker buildx build --push --platform linux/arm64/v8,linux/amd64 --tag  <your user name>/image_name:<your tag> .
```

If you're building a container that uses common files (e.g., the etl_pipeline containers), then you'd run this command from the etl_pipeline folder and include the path to the Dockerfile with the --file parameter 

```
docker buildx build --push --platform linux/arm64/v8,linux/amd64  --file finnhub/Dockerfile --tag  markhamlee/finnhub_stock_etl:latest .

```

Note: replace the name of my Dockerhub repo with your own