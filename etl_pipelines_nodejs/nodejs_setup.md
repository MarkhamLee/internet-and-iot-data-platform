### Setting up a new Node Project

1) Create directory and run the following to initialize the project, this presumes you have node, npm and npx already installed.

~~~
npm init -y
~~~
2) Use prior projects as a guide to setup package.json, just copy it to start so you don't run into issues with importing functions from other files. Run the command below to basically install packages based on the packages.json, run the command again to install any additional packages you need.

~~~
NPM install
~~~

3) Install TypeScript and Jest

~~~
npm install typescript jest ts-jest @types/jest --save-dev
~~~

4) Use a prior project as a guide to create tsconfig.json file 

5) Create a jest.config.js file with the following in it:

~~~
module.exports = {
  preset: "ts-jest",
  testEnvironment: "node",
};
~~~

6) Add "test" to the scripts section of your package.json file 

~~~
"test": "jest"
~~~

