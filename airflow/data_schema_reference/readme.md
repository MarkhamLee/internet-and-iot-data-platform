### Data Schema Reference

This folder contains json files used to validate the payloads returned by the API calls, the jsonschema library compares the fields and data types specified in the schema file with the json payload returned by the API. If things don't match, the process will error out, trigger a task failure, which will then trigger a Slack alert. Note: you don't have to match or provide validation data for every field in the incoming payload, you can just include a subset/the fields that are important to you. 

