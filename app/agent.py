import sys
from pathlib import Path
from .fetcher import fetch
from .analyzer import analyze
from .generator import generate
from .utils import slugify, save_markdown

def run(url: str) -> Path:
    print(f"→ Validating URL: {url}")
    # Basic validation
    if not url.startswith("http://") and not url.startswith("https://"):
        print("Error: URL must start with http:// or https://")
        sys.exit(1)
        
    print("→ Fetching live content (GitHub API or webcmd → httpx fallback)...")
    try:
        fetched_data = fetch(url)
    except Exception as e:
        print(f"Error fetching content: {e}")
        sys.exit(1)
        
    print("→ Analyzing with Groq → structured JSON...")
    try:
        analysis_data = analyze(fetched_data)
    except Exception as e:
        print(f"Error during analysis: {e}")
        sys.exit(1)
        
    print("→ Generating full Launch Kit + caption with Groq...")
    try:
        generated_data = generate(analysis_data)
    except Exception as e:
        print(f"Error during generation: {e}")
        sys.exit(1)
        
    print("→ Saving to output/{slug}-launch-kit.md...")
    slug = slugify(fetched_data["title"])
    if not slug:
        slug = "demo-forge"
    try:
        output_path = save_markdown(generated_data.markdown, slug)
    except Exception as e:
        print(f"Error saving markdown: {e}")
        sys.exit(1)
        
    print("→ Finished!")
    print(f"\n✓ Caption:\n{generated_data.caption}\n")
    return output_path
