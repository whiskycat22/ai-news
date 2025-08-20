# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from crew_agent import run_crew
import json

app = FastAPI(title="AI News Agent")

class TopicRequest(BaseModel):
    topic: str

class ArticleResponse(BaseModel):
    topic: str
    title: str
    subtitle: str
    seo_description: str
    sections: list
    markdown: str

@app.post("/generate", response_model=ArticleResponse)
def generate(req: TopicRequest):
    try:
        # Run the Crew workflow
        markdown_content = run_crew(req.topic)

        # Try to parse JSON from markdown (Crew output may be mixed)
        try:
            # Expecting the Crew LLM to output a JSON object with keys: title, subtitle, seo, sections, markdown
            article_json = json.loads(markdown_content)
        except Exception:
            # Fallback: if not JSON, wrap the markdown as is
            article_json = {
                "title": req.topic,
                "subtitle": "",
                "seo_description": "",
                "sections": [],
                "markdown": markdown_content
            }

        return {
            "topic": req.topic,
            "title": article_json.get("title", req.topic),
            "subtitle": article_json.get("subtitle", ""),
            "seo_description": article_json.get("seo", ""),
            "sections": article_json.get("sections", []),
            "markdown": article_json.get("markdown", markdown_content)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
