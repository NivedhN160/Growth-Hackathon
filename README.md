# DemoForge

An unattended agent that produces high-quality, publish-ready explainers from any public URL.

## Setup
```bash
python -m venv .venv
# Activate venv:
# On Windows: .\.venv\Scripts\activate
# On Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```

## Run
```bash
python main.py --url https://github.com/owner/repo
# or
python main.py --url https://any-product-page.com
```
Note: `webcmd` is preferred for product pages but not required.

## The Five Required Fields
1. **ICP**: Technical founders, indie hackers, and developer-tool teams who need to turn repositories and product pages into shareable content quickly.
2. **Hypothesis**: An unattended agent that produces high-quality, publish-ready explainers from any public URL will increase the distribution and perceived polish of technical products.
3. **Channel**: Direct live demo + the generated Markdown posted to LinkedIn, X, blogs, and Product Hunt.
4. **Conversion path**: Judge/user pastes URL → DemoForge generates Markdown → content is published → drives stars, sign-ups, or inbound interest.
5. **Success metric**: Percentage of generated documents that a stranger would publish with zero or minimal edits.

## Output format
The script outputs a full Launch Kit including:
- Product Name & Strongest Hook
- What it is
- Problem it solves
- Key features
- How it works (technical overview)
- Getting started (commands)
- Who it’s for
- Why this is interesting right now
- Social Caption
- Alternative Hooks
