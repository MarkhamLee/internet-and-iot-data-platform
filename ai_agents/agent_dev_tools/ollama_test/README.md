## Testing Ollama Connection

Simple code that uses FastAPI and Lanchain to set up a local server that you can then use to test an Ollama instance. 

1. Set the environmental variables for the ollama instance's URL 

2. Run the following command from this folder to run Langchain behind FastAPI 

```
uvicorn main:app --reload --host 0.0.0.0 --port 8000

```

3. Use curl or a Postman (get command) to hit server_ip:8000/health to verify everything works

4. Use postman to send the json below to the server_ip:8000/go endpoint 

~~~
{
  "input": "What is 42 plus 58?"
}
~~~

The response should look like the below:

~~~

{
    "output": "42 plus 58 equals 100."
}
~~~