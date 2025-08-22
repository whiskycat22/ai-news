import warnings
warnings.filterwarnings("ignore")
from crewai import Agent, Task, Crew, LLM
import json
import os
from dotenv import load_dotenv

load_dotenv()
os.environ["GOOGLE_CLOUD_PROJECT"] = "proudly-artificial-469010"

llm = LLM(
    model="gemini-2.5-flash-lite",
    temperature=0.7,
    timeout=180,
    max_tokens=5000,
    top_p=0.9,
    frequency_penalty=0.1,
    presence_penalty=0.1,
    response_format={"type": "json"},  # enforce JSON at API level
    provider="vertex_ai",
    seed=42
)

# Planner: outlines the article
planner = Agent(
    role="Content Planner",
    goal="Plan a detailed news article about {topic}. Output as JSON with: title, subtitle, seo, and sections (list of strings).",
    backstory="You create structured content plans for news articles.",
    allow_delegation=False,
    verbose=False,
    llm=llm
)

# Writer: writes full article
writer = Agent(
    role="Content Writer",
    goal="Write a news article in Markdown based on the content plan. Include title, subtitle, seo, and sections.",
    backstory="You are a journalist writing high-quality articles.",
    allow_delegation=False,
    verbose=False,
    llm=llm
)

# Editor: outputs final valid JSON only
editor = Agent(
    role="Editor",
    goal=(
        "Convert the Markdown article into a JSON object ONLY. "
        "Use this schema:\n"
        "{\n"
        '  "title": string,\n'
        '  "subtitle": string,\n'
        '  "sections": [\n'
        '    {"heading": string, "content": string}\n'
        '  ]\n'
        "}\n"
        "Return nothing except valid JSON. Do not include markdown, explanations, or commentary."
    ),
    backstory="You are an editor who ensures the final article is clean, structured JSON.",
    allow_delegation=False,
    verbose=False,
    llm=llm
)

# Tasks
plan_task = Task(
    description="Plan the article for {topic} with JSON (title, subtitle, seo, sections).",
    expected_output="JSON with keys: title, subtitle, seo, sections (list of section titles).",
    agent=planner
)

write_task = Task(
    description="Write the full article in Markdown from the plan.",
    expected_output="Markdown string with title, subtitle, seo, and sections.",
    agent=writer
)

edit_task = Task(
    description="Convert the Markdown article into structured JSON (title, subtitle, sections).",
    expected_output="Valid JSON only (no markdown, no explanations).",
    agent=editor
)

# Crew
crew = Crew(
    agents=[planner, writer, editor],
    tasks=[plan_task, write_task, edit_task],
    verbose=False
)

def extract_final_json(s: str) -> dict:
    """Extract the last valid JSON object from a string."""
    decoder = json.JSONDecoder()
    last_obj = None
    idx = 0

    while idx < len(s):
        try:
            obj, end = decoder.raw_decode(s[idx:])
            last_obj = obj
            idx += end
        except json.JSONDecodeError:
            idx += 1

    if last_obj is None:
        raise ValueError("No valid JSON found in string")
    return last_obj

def run_crew(topic: str) -> dict:
    result = crew.kickoff(inputs={"topic": topic})
    editor_output = result.tasks_output[-1]

    output_str = getattr(editor_output, "raw", None) \
                 or getattr(editor_output, "output", None) \
                 or getattr(editor_output, "text", None)

    if not output_str:
        raise ValueError("Editor task produced no usable output")

    try:
        article_json = extract_final_json(output_str)
    except Exception:
        article_json = {
            "title": topic,
            "subtitle": "",
            "sections": [{"heading": "Draft", "content": output_str}]
        }

    return article_json
