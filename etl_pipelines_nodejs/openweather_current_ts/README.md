### Basic Instructions

* Make sure you have a recent copy of node, npm and npx installed
* Clone the repo/copy the files, note: you don't need the .js files, those will be re-created when you compile the TypeScript code and are just there for reference.
* Run 'NPM install' to install the packages 
* Compile the TypeScript code from the ../src directory with 'npx tsc index.ts' 
* Run the files locally by:
    * Creating all the environmental variables for your InfluxDB instance, creating your own OpenWeather API key, etc. 
    * Running "ts-node index.ts" or "node index.js" will run the file
* If you run into issues, in particular getting errors for "process.env" or the imports not working... 
    * Re-run NPM install from the directory with the package.json file
    * Re-compile the code by running 'npx tsc index.ts' 
    