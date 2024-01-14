#### ETL Containers & Scripts

Once I decided to start experimenting with different Airflow executors and other tools to build ETL pipelines, I decided to rebuild all of my ETL pipelines (originally as Airflow DAGs) into containers a couple of reasons: 
1) Most ETL tools are just container orchestrators 
2) Once you have things defined as a container, you have stand-alone scripts you can deploy for ETL purposes as well
3) I really like Airflow, but the DAG format is not very portable outside of Airflow, so moving to containers and avoiding it as much as possible is just a good idea. 

This folder holds fully operational ETL containers that are pretty much ready to go, aside from needing the end user to setup credentials for the respective APIs, have a database setup (InfluxDB or Postgres) to store the data, etc. I.e. build the image, add the right environmental variables for databases, APIs and the like, deploy the container and you're good to go. 

A lot of these ETL processes use a lot of common code for writing to DBs, logging, pinging different endpoints from the same API provider, etc., so I've written the Dockerfiles to pull those scripts from common folders (see: "etl_library" and "openweather_library"). My plan is to use this approach as the basis for a CI/CD pipelines that can build images and deploy containers into any orchestration tool, without my having to make too many changes on my end. 

Keep in mind that building Docker images from different folders like this (namely from the parent folder the Docker file is in), is slightly tricky because when using the standard Docker build command, the Dockerfile can't copy files from the parent folder for security reasons. SO, to build the images you'll need to run a command like the following from the etl_pipelines folder so the parent folder is the "Docker build context": 

~~~
docker build -t openweather_airquality:latest -f openweather_air_quality/Dockerfile .
~~~

This command will set the parent folder with the common libraries as the "Docker build context", which will allow you to copy all the required files into your image. 

Note on testing, the testing process was:
* Just running the python scripts locally
* Building the images and then via K8s cron jobs and/or via Portainer

Once the above was fine, I would then deploy them with one or more orchestration tools. 

