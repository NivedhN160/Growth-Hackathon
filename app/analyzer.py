import json
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List
from groq import Groq
from .config import GROQ_API_KEY, GROQ_MODEL, MAX_CONTENT_CHARS
from .utils import truncate

class AnalysisOutput(BaseModel):
    product_name: str
    one_line_hook: str
    what_it_is: str
    problem_it_solves: str
    key_features: List[str]
    how_it_works: str
    getting_started_commands: str
    target_audience: str
    why_it_matters_now: str
    alternative_hooks: List[str] = Field(..., min_length=3, max_length=3)

def analyze(fetched_data: dict) -> AnalysisOutput:
    client = Groq(api_key=GROQ_API_KEY)
    
    system_prompt = Path("prompts/system.txt").read_text(encoding="utf-8")
    analyze_prompt = Path("prompts/analyze.txt").read_text(encoding="utf-8")
    
    truncated_content = truncate(fetched_data["content"], MAX_CONTENT_CHARS)
    
    user_message = f"{analyze_prompt}\n\nSource Material:\n{truncated_content}"
    
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        response_format={"type": "json_object"},
        temperature=0.2
    )
    
    result_text = response.choices[0].message.content
    try:
        data = json.loads(result_text)
        return AnalysisOutput(**data)
    except Exception as e:
        if result_text.startswith("```json"):
            result_text = result_text[7:-3].strip()
            data = json.loads(result_text)
            return AnalysisOutput(**data)
        raise ValueError(f"Failed to parse analysis output: {e}")
