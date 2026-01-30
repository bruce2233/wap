#!/usr/bin/env python3
import argparse
import json
import os
import re
import textwrap
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

from bs4 import BeautifulSoup
from pypdf import PdfReader


ARXIV_ID_RE = re.compile(r"\b\d{4}\.\d{4,5}(v\d+)?\b")


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-") or "paper"


def parse_issue_body(body: str) -> dict:
    def extract(section: str) -> str:
        pattern = rf"### {re.escape(section)}\s*([\s\S]*?)(?:\n### |\Z)"
        match = re.search(pattern, body)
        if not match:
            return ""
        return match.group(1).strip()

    return {
        "paper_query": extract("Paper query"),
        "slug": extract("Slug (optional)"),
        "notes": extract("Notes (optional)"),
    }


def github_api_get(url: str, token: str):
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_issue(issue_number: str) -> dict:
    repo = os.environ.get("GITHUB_REPOSITORY")
    token = os.environ.get("GITHUB_TOKEN")
    if not repo or not token:
        raise RuntimeError("GITHUB_REPOSITORY or GITHUB_TOKEN not set")
    url = f"https://api.github.com/repos/{repo}/issues/{issue_number}"
    return github_api_get(url, token)


def find_arxiv_id(text: str) -> str:
    match = ARXIV_ID_RE.search(text or "")
    if match:
        return match.group(0)
    return ""


def fetch_arxiv_metadata(arxiv_id: str) -> dict:
    url = f"https://export.arxiv.org/api/query?id_list={arxiv_id}"
    with urllib.request.urlopen(url) as resp:
        data = resp.read().decode("utf-8")
    root = ET.fromstring(data)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    entry = root.find("atom:entry", ns)
    if entry is None:
        return {}
    title = (entry.findtext("atom:title", default="", namespaces=ns) or "").strip()
    summary = (entry.findtext("atom:summary", default="", namespaces=ns) or "").strip()
    published = (entry.findtext("atom:published", default="", namespaces=ns) or "").strip()
    authors = [a.findtext("atom:name", default="", namespaces=ns).strip() for a in entry.findall("atom:author", ns)]
    return {
        "title": " ".join(title.split()),
        "summary": " ".join(summary.split()),
        "published": published[:10],
        "authors": authors,
    }


def extract_pdf_text(arxiv_id: str, max_pages: int = 6, max_chars: int = 12000) -> str:
    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    tmp_path = Path("/tmp") / f"{arxiv_id}.pdf"
    urllib.request.urlretrieve(pdf_url, tmp_path)
    reader = PdfReader(str(tmp_path))
    texts = []
    for i, page in enumerate(reader.pages[:max_pages]):
        try:
            texts.append(page.extract_text() or "")
        except Exception:
            continue
    text = "\n".join(texts)
    return text[:max_chars]


def openai_chat(system: str, user: str, model: str, max_tokens: int = 4500) -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.2,
        "max_tokens": max_tokens,
    }

    req = urllib.request.Request("https://api.openai.com/v1/chat/completions")
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")

    with urllib.request.urlopen(req, data=json.dumps(payload).encode("utf-8")) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    return data["choices"][0]["message"]["content"].strip()


def build_version_links(slug: str) -> dict:
    return {
        "hs-en": f"/papers/{slug}/hs-en.html",
        "grad-en": f"/papers/{slug}/grad-en.html",
        "hs-zh": f"/papers/{slug}/hs-zh.html",
        "grad-zh": f"/papers/{slug}/grad-zh.html",
    }


def generate_html(version: str, metadata: dict, context_text: str, slug: str, prompt_text: str, notes: str) -> str:
    lang_map = {
        "hs-en": ("en", "High School"),
        "grad-en": ("en", "Graduate"),
        "hs-zh": ("zh-Hans", "高中"),
        "grad-zh": ("zh-Hans", "研究生"),
    }
    lang, level = lang_map[version]

    links = build_version_links(slug)

    system = (
        "You generate a complete HTML document for a WAP paper page. "
        "Follow the paper's original structure and section order; do not force generic headings. "
        "Always include a paper facts block, resource links, and a version switcher. "
        "Use absolute paths for CSS/JS and internal links. Output HTML only, no code fences."
    )

    user = textwrap.dedent(
        f"""
        Version: {version}
        Language: {lang}
        Audience level: {level}
        Slug: {slug}

        Required assets:
        - CSS: /papers/{slug}/styles.css
        - JS: /papers/{slug}/script.js

        Version switcher links:
        - HS EN: {links['hs-en']}
        - Grad EN: {links['grad-en']}
        - HS ZH: {links['hs-zh']}
        - Grad ZH: {links['grad-zh']}

        Metadata:
        - Title: {metadata.get('title','')}
        - Authors: {", ".join(metadata.get('authors', []))}
        - Date: {metadata.get('published','')}
        - Venue: {metadata.get('venue','arXiv')}
        - arXiv ID: {metadata.get('arxiv_id','')}

        Abstract:
        {metadata.get('summary','')}

        Extracted paper text (for structure):
        {context_text}

        Extra notes:
        {notes or "(none)"}

        Prompt requirements:
        {prompt_text}

        Output a full HTML document. Use classes from the existing WAP styles (topbar, hero, hero-card, card, content-grid, section-header, resources, button-row, btn, footer, etc.).
        Provide a version switcher section with links to the other three versions.
        Do not include inline CSS. Use the linked stylesheet.
        """
    ).strip()

    max_tokens = 3200 if version.startswith("hs") else 5200
    return openai_chat(system, user, os.environ.get("OPENAI_MODEL", "gpt-4o-mini"), max_tokens=max_tokens)


def generate_card_summaries(metadata: dict, prompt_text: str, notes: str) -> dict:
    system = "Generate short summaries for index cards."
    user = textwrap.dedent(
        f"""
        Paper title: {metadata.get('title','')}
        Abstract: {metadata.get('summary','')}
        Notes: {notes or "(none)"}

        Provide 4 one-line summaries:
        - hs_en
        - grad_en
        - hs_zh
        - grad_zh

        Each should be a single sentence suitable for a card teaser.
        """
    ).strip()

    content = openai_chat(system, user, os.environ.get("OPENAI_MODEL", "gpt-4o-mini"), max_tokens=600)
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    result = {
        "hs_en": "",
        "grad_en": "",
        "hs_zh": "",
        "grad_zh": "",
    }
    for line in lines:
        for key in result.keys():
            if line.lower().startswith(key):
                result[key] = line.split(":", 1)[-1].strip()
    return result


def write_index_page(folder: Path, slug: str):
    links = build_version_links(slug)
    html = f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>WAP Paper Variants</title>
  <link rel=\"icon\" href=\"/logo.jpg\" type=\"image/jpeg\" />
  <link rel=\"stylesheet\" href=\"/papers/{slug}/styles.css\" />
</head>
<body>
  <main class=\"page\">
    <section class=\"hero\">
      <div class=\"hero-text\">
        <p class=\"eyebrow\">WAP Paper Page</p>
        <h1>Choose a version</h1>
        <p class=\"lede\">Four standalone pages: HS/Grad × EN/中文.</p>
      </div>
    </section>
    <section class=\"content-grid\">
      <a class=\"card\" href=\"{links['hs-en']}\"><h3>HS · EN</h3></a>
      <a class=\"card\" href=\"{links['grad-en']}\"><h3>Grad · EN</h3></a>
      <a class=\"card\" href=\"{links['hs-zh']}\"><h3>高中 · 中文</h3></a>
      <a class=\"card\" href=\"{links['grad-zh']}\"><h3>研究生 · 中文</h3></a>
    </section>
  </main>
</body>
</html>"""
    (folder / "index.html").write_text(html, encoding="utf-8")


def update_index(repo_path: Path, slug: str, metadata: dict, summaries: dict, tags: list):
    index_path = repo_path / "index.html"
    soup = BeautifulSoup(index_path.read_text(encoding="utf-8"), "lxml")
    paper_list = soup.find("div", {"id": "paper-list"})
    if paper_list is None:
        raise RuntimeError("paper-list not found in index.html")

    href = f"/{slug}"
    if paper_list.find("a", {"href": href}):
        return

    card = soup.new_tag("a", attrs={
        "class": "paper-card",
        "href": href,
        "data-title": f"{metadata.get('title','')} {metadata.get('title_zh','')}",
        "data-tags": " ".join(tags),
        "data-arxiv": metadata.get("arxiv_id", ""),
    })

    h3 = soup.new_tag("h3")
    span_en = soup.new_tag("span", attrs={"class": "lang", "data-lang": "en"})
    span_en.string = metadata.get("title", "")
    span_zh = soup.new_tag("span", attrs={"class": "lang", "data-lang": "zh", "lang": "zh-Hans"})
    span_zh.string = metadata.get("title_zh", "")
    h3.append(span_en)
    h3.append(span_zh)

    hs = soup.new_tag("div", attrs={"class": "level", "data-level": "hs"})
    hs_en = soup.new_tag("span", attrs={"class": "lang", "data-lang": "en"})
    hs_en.string = summaries.get("hs_en", "")
    hs_zh = soup.new_tag("span", attrs={"class": "lang", "data-lang": "zh", "lang": "zh-Hans"})
    hs_zh.string = summaries.get("hs_zh", "")
    hs.append(hs_en)
    hs.append(hs_zh)

    grad = soup.new_tag("div", attrs={"class": "level", "data-level": "grad"})
    grad_en = soup.new_tag("span", attrs={"class": "lang", "data-lang": "en"})
    grad_en.string = summaries.get("grad_en", "")
    grad_zh = soup.new_tag("span", attrs={"class": "lang", "data-lang": "zh", "lang": "zh-Hans"})
    grad_zh.string = summaries.get("grad_zh", "")
    grad.append(grad_en)
    grad.append(grad_zh)

    pill_row = soup.new_tag("div", attrs={"class": "pill-row"})
    pill = soup.new_tag("span", attrs={"class": "pill"})
    pill.string = f"arXiv {metadata.get('arxiv_id','')}" if metadata.get("arxiv_id") else "Paper"
    pill_row.append(pill)

    card.append(h3)
    card.append(hs)
    card.append(grad)
    card.append(pill_row)

    paper_list.insert(0, card)
    index_path.write_text(str(soup), encoding="utf-8")


def ensure_assets(repo_path: Path, slug: str):
    base_dir = repo_path / "papers" / "learning-to-discover-at-test-time"
    target_dir = repo_path / "papers" / slug
    target_dir.mkdir(parents=True, exist_ok=True)

    styles_path = target_dir / "styles.css"
    script_path = target_dir / "script.js"

    if not styles_path.exists():
        if (base_dir / "styles.css").exists():
            base_css = (base_dir / "styles.css").read_text(encoding="utf-8")
        else:
            base_css = ""
        extra_css = textwrap.dedent(
            """
            .paper-body {
              display: flex;
              flex-direction: column;
              gap: 24px;
            }

            .version-switch {
              display: flex;
              flex-wrap: wrap;
              gap: 10px;
              margin-top: 12px;
            }

            .version-pill {
              padding: 6px 12px;
              border-radius: 999px;
              background: rgba(21, 25, 34, 0.06);
              font-size: 0.85rem;
            }
            """
        )
        styles_path.write_text(base_css + "\n" + extra_css, encoding="utf-8")

    if not script_path.exists():
        if (base_dir / "script.js").exists():
            script = (base_dir / "script.js").read_text(encoding="utf-8")
        else:
            script = "// Reserved for per-paper interactions.\n"
        script_path.write_text(script, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue", required=True)
    parser.add_argument("--repo-path", default="/Users/yunpeng.zhang2/app/wap")
    parser.add_argument("--prompt-file", required=True)
    args = parser.parse_args()

    issue = fetch_issue(args.issue)
    parsed = parse_issue_body(issue.get("body", ""))
    paper_query = parsed.get("paper_query") or issue.get("title", "")
    slug = parsed.get("slug") or ""
    notes = parsed.get("notes")

    arxiv_id = find_arxiv_id(paper_query)
    metadata = {
        "title": paper_query,
        "title_zh": "",
        "summary": "",
        "authors": [],
        "published": "",
        "venue": "arXiv",
        "arxiv_id": arxiv_id,
    }

    context_text = ""

    if arxiv_id:
        meta = fetch_arxiv_metadata(arxiv_id)
        metadata.update(meta)
        metadata["arxiv_id"] = arxiv_id
        try:
            context_text = extract_pdf_text(arxiv_id)
        except Exception:
            context_text = ""

    if not metadata.get("title_zh"):
        metadata["title_zh"] = metadata.get("title", "")

    if not slug:
        slug = slugify(metadata.get("title") or paper_query)

    repo_path = Path(args.repo_path)
    paper_dir = repo_path / "papers" / slug

    ensure_assets(repo_path, slug)

    prompt_text = Path(args.prompt_file).read_text(encoding="utf-8")

    versions = ["hs-en", "grad-en", "hs-zh", "grad-zh"]
    for version in versions:
        html = generate_html(version, metadata, context_text, slug, prompt_text, notes)
        out_path = paper_dir / f"{version}.html"
        out_path.write_text(html, encoding="utf-8")

    write_index_page(paper_dir, slug)

    summaries = generate_card_summaries(metadata, prompt_text, notes)
    tags = ["WAP"]
    update_index(repo_path, slug, metadata, summaries, tags)

    print(f"Generated pages for {slug}")


if __name__ == "__main__":
    main()
