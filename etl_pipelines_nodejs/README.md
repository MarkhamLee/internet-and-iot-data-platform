## Node.js ETL Pipelines

For practice/experience building out Node.JS versions of most if not all of the ETLs I built in Python. Given my approach of deploying all ETLs in Docker containers, it just made sense to build them in multiple languages to get experience with building deploying ETL containers on tools like Airflow and Argo Workflow in languages other than Python. To get more details on the overall approach, you can read more in the [Readme](https://github.com/MarkhamLee/finance-productivity-iot-informational-weather-dashboard/tree/main/etl_pipelines) in my primary ETL folder. 

Regardless of the language being used, certain core tenants always apply:

* All ETLs are built using Docker containers
* Leverage shared libraries as much as possible, meaning files/classes/methods for things like validating json, writing to Postgres or InfluxDB, etc., can be shared among multiple ETLs. In this instance, the shared files are in the "common" folder.
* Docker builds are automated via GitHub Actions, and all containers are built for both amd64 and arm64 architectures
* Automated testing via unit testing libraries like jest (Node.js) and Unit Test (Python)
* Alerts are sent via Slack if any problems occur 
* Strict type checking and data validation of API response payloads, prior to the data being written to InfluxDB or PostgreSQL. In some cases the data is checked after the API response, and again once it has been parsed/transformed. 

### Building & Transpiling

* the folders for the TypeScript ETLs only contain the source files, you will have to transpile them into JavaScript to run them. 
* I used npm as the package manager
* **Key commands:** 
  * Run "npm install" build all the packages when you first setup the project. 
  * "npx tsc --init" to initialize the project
  * "npx tsc" to transpile the .ts files into .js ones
  * "node index.js" to run the ETL
  * You should also run "npm install" when you update package versions, for example:
    * You update a package version number in /common/package.json to address a security vulnerability or to use new functionality. You would then run "npm install" from that folder, in order to update the package-lock.json everyplace that package is referenced. 
    * After the above run "npm audit fix" to address any other known security vulnerabilities.
    * Next, check it into GitHub and containers that use that file will be rebuilt via a GitHub Action and then deployed to Docker Hub.
* When cloning these folders, you will need to run the NPM install command in the "common" folder as well as the folder for an individual ETL
* The following has to be added to the tsconfig.json for a given project/ETL folder so it can use the common files 

~~~
  "references": [
    {
      "path": "../common"
    }
  ]
~~~

