# Web Any Paper (WAP)

WAP is a static site that renders bilingual (EN/中文) and dual-level (HS/Grad) paper pages from JSON.

## Structure

- `index.html` — SPA router + layout
- `app.js` — rendering logic
- `data/papers.json` — index list
- `data/papers/<slug>.json` — per-paper content
- `vercel.json` — rewrite for `/<slug>` routing

## Add a paper

1) Create `data/papers/<slug>.json` (copy an existing file).
2) Update `data/papers.json` with the new entry.
3) Push to GitHub — Vercel deploys automatically.

Optional helper:

```
node scripts/add-paper.js --slug my-paper --title-en "Title" --title-zh "标题" --arxiv 1234.56789
```

## Local preview

```
python3 -m http.server 8000
```

Then open `http://localhost:8000`.
