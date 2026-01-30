---
name: wap-paper-page
description: "Create and deploy WAP standalone paper pages (HS/Grad × EN/中文) for a specified paper; use when asked to generate a new WAP paper page, update the WAP index, and push to bruce2233/wap."
---

# WAP Paper Page

## Overview

Create a new WAP paper page with **four standalone variants** (HS/Grad × EN/中文), update the WAP index, and push changes to the `bruce2233/wap` repo.

## Workflow

1) Read `references/wap_prompt.md` for the full prompt and required output structure.
2) Use `web.run` to verify paper metadata, methods, results, and resources.
3) Create `/papers/<slug>/` with:
   - `index.html` (landing + links to 4 variants)
   - `hs-en.html`, `grad-en.html`, `hs-zh.html`, `grad-zh.html`
   - `styles.css`, `script.js`
4) Use **absolute paths** for assets and links (e.g., `/papers/<slug>/styles.css`).
5) Update `index.html` in the WAP root to add a new paper card.
6) `git add/commit/push` to `bruce2233/wap` without printing secrets.
7) Return final URLs for the slug and all four variants.

## Resources

- `references/wap_prompt.md` — authoritative prompt text and requirements.
