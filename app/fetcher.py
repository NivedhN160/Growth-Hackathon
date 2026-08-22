import httpx
from bs4 import BeautifulSoup
import html2text
import subprocess
import json
import shutil
from .utils import is_github_url, extract_owner_repo, clean_text

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0.0.0 Safari/537.36"
)

def fetch_github(url: str) -> dict:
    owner, repo = extract_owner_repo(url)
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    readme_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/README.md"

    headers = {"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"}

    with httpx.Client(headers=headers, timeout=20.0, follow_redirects=True) as client:
        resp = client.get(api_url)
        resp.raise_for_status()
        data = resp.json()

        readme_resp = client.get(readme_url)
        if readme_resp.status_code == 404:
            readme_url = f"https://raw.githubusercontent.com/{owner}/{repo}/master/README.md"
            readme_resp = client.get(readme_url)

        readme_content = readme_resp.text if readme_resp.status_code == 200 else ""

    content = (
        f"Repository: {data.get('name')}\n"
        f"Description: {data.get('description')}\n"
        f"Stars: {data.get('stargazers_count')}\n"
        f"Language: {data.get('language')}\n"
        f"Topics: {', '.join(data.get('topics', []))}\n"
        f"Homepage: {data.get('homepage')}\n\n"
        f"README:\n{readme_content}"
    )

    return {
        "source_type": "github",
        "url": url,
        "title": data.get("name") or "",
        "description": data.get("description") or "",
        "content": clean_text(content),
    }


def fetch_with_webcmd(url: str) -> dict | None:
    """
    Prefer webcmd when it is installed.
    Uses a short-lived browser session to extract title + main text.
    Returns None on any failure so we can fall back to httpx.
    """
    if not shutil.which("webcmd"):
        return None

    try:
        # Create a temporary session
        create = subprocess.run(
            ["webcmd", "session", "create", "-f", "json"],
            capture_output=True,
            text=True,
            timeout=15,
            check=True,
        )
        session_info = json.loads(create.stdout)
        session_id = session_info.get("id") or session_info.get("session_id")
        if not session_id:
            return None

        # Simple extraction script
        js = f"""
        await page.goto("{url}", {{ waitUntil: "domcontentloaded", timeout: 20000 }});
        const title = await page.title();
        const description = await page.evaluate(() => {{
            const m = document.querySelector('meta[name="description"]');
            return m ? m.content : "";
        }});
        const text = await page.evaluate(() => document.body.innerText.slice(0, 15000));
        return JSON.stringify({{ title, description, content: text }});
        """

        run = subprocess.run(
            ["webcmd", "--session", session_id, "browser", "run", "--stdin"],
            input=js,
            capture_output=True,
            text=True,
            timeout=35,
            check=True,
        )

        # Always try to close the session
        subprocess.run(
            ["webcmd", "session", "close", session_id],
            capture_output=True,
            timeout=10,
        )

        raw = run.stdout.strip()
        # webcmd may wrap the result; try to parse the last JSON object
        data = json.loads(raw)
        if isinstance(data, str):
            data = json.loads(data)

        return {
            "source_type": "product",
            "url": url,
            "title": (data.get("title") or "").strip(),
            "description": (data.get("description") or "").strip(),
            "content": clean_text(data.get("content") or ""),
        }
    except Exception:
        return None


def fetch_product_page(url: str) -> dict:
    # 1. Prefer webcmd
    webcmd_result = fetch_with_webcmd(url)
    if webcmd_result and webcmd_result.get("content"):
        return webcmd_result

    # 2. Fallback: httpx + BeautifulSoup
    headers = {"User-Agent": USER_AGENT}
    with httpx.Client(headers=headers, timeout=20.0, follow_redirects=True) as client:
        resp = client.get(url)
        resp.raise_for_status()
        html = resp.text

    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else ""
    meta_desc = ""
    desc_tag = soup.find("meta", attrs={"name": "description"})
    if desc_tag and desc_tag.get("content"):
        meta_desc = desc_tag["content"].strip()

    converter = html2text.HTML2Text()
    converter.ignore_links = False
    converter.ignore_images = True
    content = converter.handle(html)

    combined = f"Title: {title}\nDescription: {meta_desc}\n\n{content}"

    return {
        "source_type": "product",
        "url": url,
        "title": title,
        "description": meta_desc,
        "content": clean_text(combined),
    }


def fetch(url: str) -> dict:
    if is_github_url(url):
        return fetch_github(url)
    return fetch_product_page(url)
