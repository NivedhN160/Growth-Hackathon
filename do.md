**DemoForge — Perfect Architecture Plan**

---

### 1. One-sentence architecture

DemoForge is a linear, unattended pipeline that turns any public URL into a complete Launch Kit by combining deterministic fetching, structured LLM analysis, and controlled generation — with zero human steering after the command starts.

---

### 2. High-level flow

```
URL
  │
  ▼
┌─────────────────┐
│   main.py       │  CLI entry (Typer)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   agent.py      │  Orchestrator (single run())
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
fetcher   analyzer → generator
    │         │           │
    └────┬────┘           │
         ▼                ▼
      utils.py      output/*.md
```

Every stage is pure, typed, and fails loudly. There is no shared mutable state.

---

### 3. Layered architecture

| Layer | Responsibility | Files |
|-------|----------------|-------|
| **Interface** | Accept URL, print results, exit codes | `main.py` |
| **Orchestration** | Strict sequence, progress, error boundaries | `app/agent.py` |
| **Acquisition** | Real content from GitHub or product pages | `app/fetcher.py` |
| **Understanding** | Structured extraction via LLM | `app/analyzer.py` |
| **Creation** | Launch Kit Markdown + caption | `app/generator.py` |
| **Support** | Config, pure helpers, prompts | `config.py`, `utils.py`, `prompts/` |
| **Output** | Durable publish-ready file | `output/` |

---

### 4. Component contracts

**fetcher.py**  
Input: `url: str`  
Output:  
```python
{
  "source_type": "github" | "product",
  "url": str,
  "title": str,
  "description": str,
  "content": str   # cleaned, truncated later
}
```
Strategy:
1. GitHub → public API + raw README  
2. Product → webcmd (session + browser extract) if available  
3. Fallback → httpx + BeautifulSoup + html2text  

**analyzer.py**  
Input: fetched dict  
Output: `AnalysisOutput` (Pydantic)  
- product_name  
- one_line_hook  
- what_it_is  
- problem_it_solves  
- key_features: list[str]  
- how_it_works  
- getting_started_commands  
- target_audience  
- why_it_matters_now  
- alternative_hooks: exactly 3 strings  

**generator.py**  
Input: `AnalysisOutput`  
Output:  
```python
{
  "markdown": str,   # full Launch Kit
  "caption": str     # ≤ 280 chars
}
```

**agent.py**  
Single public function: `run(url: str) -> Path`  
Order is fixed and never changes:
1. Validate  
2. Fetch  
3. Analyze  
4. Generate  
5. Save  
6. Print caption  
7. Return path  

---

### 5. Data flow (end-to-end)

```
1. User → python main.py --url <public-url>
2. agent validates scheme (http/https)
3. fetcher returns normalised content dict
4. analyzer truncates → Groq (JSON mode) → AnalysisOutput
5. generator → Groq (JSON mode) → markdown + caption
6. utils.save_markdown → output/{slug}-launch-kit.md
7. caption printed to stdout
8. Path returned to main.py → success message
```

Two LLM calls only. No loops. No agentic replanning.

---

### 6. Design principles (why this is clean)

| Principle | How DemoForge follows it |
|-----------|---------------------------|
| Single Responsibility | Each module does one job |
| Fail fast | Missing key, bad URL, fetch error → clear exit |
| Graceful degradation | webcmd optional; httpx always works |
| Deterministic pipeline | Same stages, same order, every run |
| Typed boundaries | Pydantic models between analyzer ↔ generator |
| Zero side effects in helpers | utils are pure |
| Externalised prompts | prompts/ can be tuned without touching code |
| Free by default | Groq free tier + public APIs only |

---

### 7. External dependencies (minimal surface)

```
┌──────────────┐     ┌──────────────┐
│  GitHub API  │     │  Product URL │
└──────┬───────┘     └──────┬───────┘
       │                    │
       │              ┌─────▼─────┐
       │              │  webcmd?  │──yes──► browser extract
       │              └─────┬─────┘
       │                    │ no
       │              ┌─────▼─────┐
       │              │httpx+BS4  │
       │              └─────┬─────┘
       └────────┬───────────┘
                ▼
         cleaned content
                │
         ┌──────▼──────┐
         │    Groq     │  (2 calls)
         └──────┬──────┘
                ▼
         Launch Kit .md
```

---

### 8. Failure model

| Failure | Behaviour |
|---------|-----------|
| No GROQ_API_KEY | Hard error at import / config load |
| Invalid URL | Rejected before any network call |
| GitHub 404 / rate limit | Exception → clean message |
| webcmd missing or broken | Silent fallback to httpx |
| Product page blocked | Exception with clear reason |
| LLM returns bad JSON | Retry parse (strip fences) → then fail |
| Disk write error | Exception → non-zero exit |

No silent successes. No invented content.

---

### 9. Output contract (fixed)

Every successful run produces exactly one file:

```
output/{slug}-launch-kit.md
```

Containing:
- Title + strongest hook  
- What it is  
- Problem  
- Key features  
- How it works  
- Getting started  
- Who it’s for  
- Why interesting now  
- Ready-to-post caption  
- Three alternative hooks  

This is the only deliverable. No extra files, no side databases.

---

### 10. Why this architecture wins in a 4-hour sprint

- Linear and easy to reason about under pressure  
- Every stage can be tested independently  
- webcmd is a nice-to-have differentiator, not a hard dependency  
- Two LLM calls keep latency and free-tier usage predictable  
- Judges can run one command on an unseen URL and get a real artifact  

---

### 11. One-line summary for judges

> DemoForge is a strict four-stage pipeline (Fetch → Analyze → Generate → Save) that converts any public URL into a complete, publish-ready Launch Kit with optional webcmd-powered extraction and full free-tier operation.

This is the architecture. It is already implemented in the repo.