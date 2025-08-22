from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from crew_agent import run_crew

app = FastAPI()

# ---- Request/Response Models ----

class TopicRequest(BaseModel):
    topic: str

class Section(BaseModel):
    heading: str
    content: str

class ArticleResponse(BaseModel):
    title: str
    subtitle: str
    sections: List[Section]

@app.post("/generate", response_model=ArticleResponse)
def generate(req: TopicRequest):
    try:
        article_json = run_crew(req.topic)

        return {
            "title": article_json.get("title", req.topic),
            "subtitle": article_json.get("subtitle", ""),
            "sections": article_json.get("sections", []),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))