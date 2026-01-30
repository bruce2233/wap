#!/usr/bin/env python3
import argparse
import os
import re
import textwrap
import urllib.request
import json
from pathlib import Path


def slugify(text: str) -> str:
    text = text.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-") or "paper"


def parse_issue_body(body: str) -> dict:
    def normalize(value: str) -> str:
        value = (value or "").strip()
        if not value:
            return ""
        if value.lower() in {"_no response_", "no response"}:
            return ""
        return value

    def extract(section: str) -> str:
        pattern = rf"### {re.escape(section)}\s*([\s\S]*?)(?:\n### |\Z)"
        match = re.search(pattern, body)
        if not match:
            return ""
        return normalize(match.group(1))

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


def build_prompt(paper_query: str, slug: str, notes: str, prompt_text: str) -> str:
    return textwrap.dedent(
        f"""
        You are running inside the WAP repository. Your task is to generate a new paper page.

        Paper query: {paper_query}
        Slug: {slug}
        Notes: {notes or '(none)'}

        Follow the instructions in this file verbatim:
        skills/wap-paper-page/references/wap_prompt.md

        Requirements:
        - Use web search to read the paper and authoritative sources.
        - Produce four standalone pages (HS/Grad × EN/中文) under /papers/{slug}/.
        - Use absolute paths for assets and internal links.
        - Update the root index.html with a new paper card.
        - Keep the paper structure aligned to the original paper's narrative flow.
        """
    ).strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    issue = fetch_issue(args.issue)
    parsed = parse_issue_body(issue.get("body", ""))
    paper_query = parsed.get("paper_query") or issue.get("title", "")
    slug = parsed.get("slug") or ""
    notes = parsed.get("notes")

    if not slug:
        slug = slugify(paper_query)

    prompt_text = Path("skills/wap-paper-page/references/wap_prompt.md").read_text(encoding="utf-8")
    prompt = build_prompt(paper_query, slug, notes, prompt_text)

    Path(args.output).write_text(prompt, encoding="utf-8")
    print(f"Wrote Codex prompt to {args.output}")


if __name__ == "__main__":
    main()
