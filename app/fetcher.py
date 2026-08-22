import httpx
from bs4 import BeautifulSoup
import html2text
import subprocess
import json
from .utils import is_github_url, extract_owner_repo, clean_text

def fetch_github(url: str) -> dict:
    owner, repo = extract_owner_repo(url)
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    readme_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/README.md"
    
    with httpx.Client() as client:
        # Fetch repo details
        resp = client.get(api_url)
        resp.raise_for_status()
        data = resp.json()
        
        # Try fetching README.md, fallback to master if main doesn't exist
        readme_resp = client.get(readme_url)
        if readme_resp.status_code == 404:
            readme_url = f"https://raw.githubusercontent.com/{owner}/{repo}/master/README.md"
            readme_resp = client.get(readme_url)
            
        readme_content = ""
        if readme_resp.status_code == 200:
            readme_content = readme_resp.text
            
    content = f"Repository: {data.get('name')}\n"
    content += f"Description: {data.get('description')}\n"
    content += f"Stars: {data.get('stargazers_count')}\n"
    content += f"Language: {data.get('language')}\n"
    content += f"Topics: {', '.join(data.get('topics', []))}\n"
    content += f"Homepage: {data.get('homepage')}\n\n"
    content += f"README:\n{readme_content}"
    
    return {
        "source_type": "github",
        "url": url,
        "title": data.get("name"),
        "description": data.get("description"),
        "content": clean_text(content)
    }

def fetch_with_webcmd(url: str) -> dict | None:
    try:
        # Use webcmd if available
        result = subprocess.run(["webcmd", "extract", url], capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        return {
            "title": data.get("title", ""),
            "description": data.get("description", ""),
            "content": data.get("content", ""),
            "url": url,
            "source_type": "product"
        }
    except (subprocess.SubprocessError, FileNotFoundError, json.JSONDecodeError):
        return None

def fetch_product_page(url: str) -> dict:
    webcmd_result = fetch_with_webcmd(url)
    if webcmd_result:
        return webcmd_result
        
    with httpx.Client(follow_redirects=True) as client:
        resp = client.get(url)
        resp.raise_for_status()
        html = resp.text
        
    soup = BeautifulSoup(html, 'html.parser')
    title = soup.title.string if soup.title else ""
    meta_desc = ""
    desc_tag = soup.find('meta', attrs={'name': 'description'})
    if desc_tag:
        meta_desc = desc_tag.get('content', '')
        
    converter = html2text.HTML2Text()
    converter.ignore_links = False
    content = converter.handle(html)
    
    combined_content = f"Title: {title}\nDescription: {meta_desc}\n\n{content}"
    
    return {
        "source_type": "product",
        "url": url,
        "title": title.strip() if title else "",
        "description": meta_desc.strip(),
        "content": clean_text(combined_content)
    }

def fetch(url: str) -> dict:
    if is_github_url(url):
        return fetch_github(url)
    return fetch_product_page(url)
