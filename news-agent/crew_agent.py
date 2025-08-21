import warnings
warnings.filterwarnings("ignore")
from crewai import Agent, Task, Crew, LLM
import re
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
    response_format={"type": "json"},
    provider="vertex_ai",
    seed=42
)

# Planner: outlines the article
planner = Agent(
    role="Content Planner",
    goal="Plan a detailed news article about {topic} with title, subtitle, SEO description, and sections.",
    backstory="You create a structured content plan with sections and headlines for a news article.",
    allow_delegation=False,
    verbose=True,
    llm=llm
)

# Writer: writes article in Markdown
writer = Agent(
    role="Content Writer",
    goal="Write a news article based on the content plan. Include title, subtitle, SEO description, and sections in Markdown.",
    backstory="You are a journalist writing a high-quality news article.",
    allow_delegation=False,
    verbose=True,
    llm=llm
)

# Editor: polishes article
editor = Agent(
    role="Editor",
    goal="Proofread the Markdown article and ensure it aligns with journalistic best practices.",
    backstory="You are an editor who improves clarity, grammar, and style.",
    allow_delegation=False,
    verbose=True,
    llm=llm
)

# Tasks
plan_task = Task(
    description="Create a structured article plan for {topic} including title, subtitle, SEO description, and section headers.",
    expected_output="A JSON object with keys: title, subtitle, seo, sections (list of section titles).",
    agent=planner
)

write_task = Task(
    description="Write the full Markdown news article based on the content plan.",
    expected_output="A Markdown string including title, subtitle, SEO description, and content sections.",
    agent=writer
)

edit_task = Task(
    description="Proofread and polish the Markdown article for errors and style consistency.",
    expected_output="A polished Markdown article string.",
    agent=editor
)

# Crew
crew = Crew(
    agents=[planner, writer, editor],
    tasks=[plan_task, write_task, edit_task],
    verbose=True
)

def run_crew(topic: str) -> str:
    """
    Run the Crew workflow and return the polished Markdown news article.
    """
    result = crew.kickoff(inputs={"topic": topic})

    # Ensure string output
    if isinstance(result, dict):
        return result.get("markdown") or result.get("text") or str(result)
    elif isinstance(result, str):
        return result
    else:
        return str(result)