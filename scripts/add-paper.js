#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const args = process.argv.slice(2);
const getArg = (name) => {
  const idx = args.indexOf(`--${name}`);
  if (idx === -1) return null;
  return args[idx + 1] || null;
};

const slug = getArg('slug');
const titleEn = getArg('title-en');
const titleZh = getArg('title-zh');
const arxivId = getArg('arxiv') || '';

if (!slug || !titleEn || !titleZh) {
  console.error('Usage: node scripts/add-paper.js --slug <slug> --title-en "Title" --title-zh "标题" [--arxiv 1234.56789]');
  process.exit(1);
}

const dataDir = path.join(__dirname, '..', 'data');
const paperDir = path.join(dataDir, 'papers');
const paperPath = path.join(paperDir, `${slug}.json`);
const indexPath = path.join(dataDir, 'papers.json');

if (fs.existsSync(paperPath)) {
  console.error(`Paper already exists: ${paperPath}`);
  process.exit(1);
}

const template = {
  slug,
  title: { en: titleEn, zh: titleZh },
  subtitle: { en: 'Subtitle', zh: '副标题' },
  summary: {
    hs: { en: 'High school summary.', zh: '高中版摘要。' },
    grad: { en: 'Graduate summary.', zh: '研究生版摘要。' }
  },
  authors: [],
  arxivId,
  date: '',
  venue: '',
  tags: [],
  links: { arXiv: '', PDF: '', Project: '', Code: '' },
  sections: [
    {
      id: 'overview',
      title: { en: 'Overview', zh: '概览' },
      blocks: [
        { level: 'hs', type: 'text', text: { en: 'Add HS explanation.', zh: '添加高中版说明。' } },
        { level: 'grad', type: 'text', text: { en: 'Add grad explanation.', zh: '添加研究生版说明。' } }
      ]
    }
  ]
};

fs.writeFileSync(paperPath, JSON.stringify(template, null, 2));

const index = JSON.parse(fs.readFileSync(indexPath, 'utf8'));
index.papers.unshift({
  slug,
  title: { en: titleEn, zh: titleZh },
  summary: template.summary,
  arxivId,
  date: '',
  tags: []
});
index.updated = new Date().toISOString().slice(0, 10);

fs.writeFileSync(indexPath, JSON.stringify(index, null, 2));
console.log(`Added ${slug}`);
