import re
from pathlib import Path
from typing import Tuple

def is_github_url(url: str) -> bool:
    return url.startswith("https://github.com/") or url.startswith("http://github.com/")

def extract_owner_repo(url: str) -> Tuple[str, str]:
    # e.g. https://github.com/owner/repo
    parts = url.rstrip("/").split("/")
    if len(parts) >= 5 and "github.com" in parts[2]:
        return parts[3], parts[4]
    raise ValueError(f"Invalid GitHub URL: {url}")

def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def clean_text(text: str) -> str:
    # Remove excessive newlines and whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def truncate(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n...[Content Truncated]"

def save_markdown(content: str, slug: str) -> Path:
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    file_path = output_dir / f"{slug}-launch-kit.md"
    file_path.write_text(content, encoding="utf-8")
    return file_path
