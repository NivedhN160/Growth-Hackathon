import json
from pathlib import Path
from pydantic import BaseModel
from groq import Groq
from .config import GROQ_API_KEY, GROQ_MODEL
from .analyzer import AnalysisOutput

class GeneratorOutput(BaseModel):
    markdown: str
    caption: str

def generate(analysis: AnalysisOutput) -> GeneratorOutput:
    client = Groq(api_key=GROQ_API_KEY)
    
    PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"
    system_prompt = (PROMPTS_DIR / "system.txt").read_text(encoding="utf-8")
    generate_prompt = (PROMPTS_DIR / "generate.txt").read_text(encoding="utf-8")
    
    user_message = f"{generate_prompt}\n\nAnalysis Data:\n{analysis.model_dump_json()}"
    
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        response_format={"type": "json_object"},
        temperature=0.3
    )
    
    result_text = response.choices[0].message.content
    try:
        data = json.loads(result_text)
        return GeneratorOutput(**data)
    except Exception as e:
        if result_text.startswith("```json"):
            result_text = result_text[7:-3].strip()
            data = json.loads(result_text)
            return GeneratorOutput(**data)
        raise ValueError(f"Failed to parse generator output: {e}")
