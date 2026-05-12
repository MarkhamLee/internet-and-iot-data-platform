from fastapi import FastAPI
from pydantic import BaseModel
from agent import app_graph
from langchain_core.messages import HumanMessage

app = FastAPI()


class RunRequest(BaseModel):
    input: str


@app.post("/run")
async def run_agent(req: RunRequest):
    result = await app_graph.ainvoke(
        {"messages": [HumanMessage(content=req.input)]}
    )
    return {"output": result["messages"][-1].content}


@app.get("/health")
def health():
    return {"status": "ok"}
