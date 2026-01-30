const langButtons = document.querySelectorAll('[data-lang-btn]');
const levelButtons = document.querySelectorAll('[data-level-btn]');
const indexView = document.getElementById('index-view');
const paperView = document.getElementById('paper-view');
const paperList = document.getElementById('paper-list');
const paperCount = document.getElementById('paper-count');
const searchInput = document.getElementById('search-input');
const paperHero = document.getElementById('paper-hero');
const paperMeta = document.getElementById('paper-meta');
const paperSections = document.getElementById('paper-sections');
const backBtn = document.getElementById('back-btn');

const state = {
  papersIndex: null,
};

const setLang = (lang) => {
  document.documentElement.setAttribute('data-lang', lang);
  langButtons.forEach((btn) => {
    const isActive = btn.dataset.langBtn === lang;
    btn.setAttribute('aria-pressed', String(isActive));
  });
  try {
    localStorage.setItem('preferredLang', lang);
  } catch (err) {
    // Ignore storage errors.
  }
};

const setLevel = (level) => {
  document.documentElement.setAttribute('data-level', level);
  levelButtons.forEach((btn) => {
    const isActive = btn.dataset.levelBtn === level;
    btn.setAttribute('aria-pressed', String(isActive));
  });
  try {
    localStorage.setItem('preferredLevel', level);
  } catch (err) {
    // Ignore storage errors.
  }
};

const getInitialLang = () => {
  try {
    const saved = localStorage.getItem('preferredLang');
    if (saved === 'en' || saved === 'zh') {
      return saved;
    }
  } catch (err) {
    // Ignore storage errors.
  }
  const browserLang = navigator.language || '';
  return browserLang.toLowerCase().includes('zh') ? 'zh' : 'en';
};

const getInitialLevel = () => {
  try {
    const saved = localStorage.getItem('preferredLevel');
    if (saved === 'hs' || saved === 'grad') {
      return saved;
    }
  } catch (err) {
    // Ignore storage errors.
  }
  return 'hs';
};

const getSlug = () => {
  const path = window.location.pathname.replace(/\/$/, '');
  const parts = path.split('/').filter(Boolean);
  return parts[0] || null;
};

const setView = (view) => {
  if (view === 'index') {
    indexView.classList.remove('hidden');
    paperView.classList.add('hidden');
  } else {
    indexView.classList.add('hidden');
    paperView.classList.remove('hidden');
  }
};

const createLangElement = (tag, content) => {
  const container = document.createDocumentFragment();
  Object.entries(content).forEach(([lang, text]) => {
    const el = document.createElement(tag);
    el.className = 'lang';
    el.dataset.lang = lang;
    if (text !== null && text !== undefined) {
      el.textContent = text;
    }
    container.appendChild(el);
  });
  return container;
};

const createLevelBlock = (block) => {
  const wrapper = document.createElement('div');
  wrapper.className = 'level';
  wrapper.dataset.level = block.level;

  if (block.type === 'text') {
    Object.entries(block.text).forEach(([lang, text]) => {
      const p = document.createElement('p');
      p.className = 'lang';
      p.dataset.lang = lang;
      p.textContent = text;
      wrapper.appendChild(p);
    });
    return wrapper;
  }

  if (block.type === 'list') {
    Object.entries(block.items).forEach(([lang, items]) => {
      const ul = document.createElement('ul');
      ul.className = 'lang';
      ul.dataset.lang = lang;
      ul.classList.add('meta-list');
      items.forEach((item) => {
        const li = document.createElement('li');
        li.textContent = item;
        ul.appendChild(li);
      });
      wrapper.appendChild(ul);
    });
    return wrapper;
  }

  if (block.type === 'note') {
    Object.entries(block.text).forEach(([lang, text]) => {
      const p = document.createElement('p');
      p.className = 'lang note';
      p.dataset.lang = lang;
      p.textContent = text;
      wrapper.appendChild(p);
    });
    return wrapper;
  }

  if (block.type === 'equation') {
    Object.entries(block.lines).forEach(([lang, lines]) => {
      const pre = document.createElement('pre');
      pre.className = 'lang code';
      pre.dataset.lang = lang;
      pre.textContent = lines.join('\n');
      wrapper.appendChild(pre);
    });
    return wrapper;
  }

  return wrapper;
};

const renderIndex = (papers, filter = '') => {
  paperList.innerHTML = '';
  const search = filter.trim().toLowerCase();
  const filtered = papers.filter((paper) => {
    if (!search) return true;
    const haystack = [
      paper.slug,
      paper.title.en,
      paper.title.zh,
      paper.arxivId,
      ...(paper.tags || []),
    ]
      .join(' ')
      .toLowerCase();
    return haystack.includes(search);
  });

  filtered.forEach((paper) => {
    const card = document.createElement('a');
    card.className = 'paper-card';
    card.href = `/${paper.slug}`;
    card.addEventListener('click', (event) => {
      event.preventDefault();
      navigateTo(paper.slug);
    });

    const title = document.createElement('h3');
    title.appendChild(createLangElement('span', paper.title));

    const summaryWrapper = document.createElement('div');
    ['hs', 'grad'].forEach((level) => {
      const block = document.createElement('p');
      block.className = 'level';
      block.dataset.level = level;
      Object.entries(paper.summary[level]).forEach(([lang, text]) => {
        const span = document.createElement('span');
        span.className = 'lang';
        span.dataset.lang = lang;
        span.textContent = text;
        block.appendChild(span);
      });
      summaryWrapper.appendChild(block);
    });

    const pillRow = document.createElement('div');
    pillRow.className = 'pill-row';
    (paper.tags || []).forEach((tag) => {
      const pill = document.createElement('span');
      pill.className = 'pill';
      pill.textContent = tag;
      pillRow.appendChild(pill);
    });

    const meta = document.createElement('div');
    meta.className = 'pill';
    meta.textContent = paper.arxivId ? `arXiv ${paper.arxivId}` : 'Paper';

    card.appendChild(title);
    card.appendChild(summaryWrapper);
    card.appendChild(pillRow);
    card.appendChild(meta);

    paperList.appendChild(card);
  });

  paperCount.textContent = `${filtered.length} / ${papers.length}`;
};

const renderPaper = (paper) => {
  paperHero.innerHTML = '';
  paperMeta.innerHTML = '';
  paperSections.innerHTML = '';

  const heroText = document.createElement('div');
  const title = document.createElement('h1');
  title.className = 'paper-title';
  title.appendChild(createLangElement('span', paper.title));

  const subtitle = document.createElement('p');
  subtitle.className = 'paper-subtitle';
  subtitle.appendChild(createLangElement('span', paper.subtitle));

  const summary = document.createElement('div');
  ['hs', 'grad'].forEach((level) => {
    const block = document.createElement('p');
    block.className = 'level';
    block.dataset.level = level;
    Object.entries(paper.summary[level]).forEach(([lang, text]) => {
      const span = document.createElement('span');
      span.className = 'lang';
      span.dataset.lang = lang;
      span.textContent = text;
      block.appendChild(span);
    });
    summary.appendChild(block);
  });

  const tagRow = document.createElement('div');
  tagRow.className = 'tag-row';
  (paper.tags || []).forEach((tag) => {
    const pill = document.createElement('span');
    pill.className = 'tag';
    pill.textContent = tag;
    tagRow.appendChild(pill);
  });

  heroText.appendChild(title);
  heroText.appendChild(subtitle);
  heroText.appendChild(summary);
  heroText.appendChild(tagRow);

  const heroCard = document.createElement('div');
  heroCard.className = 'hero-card';
  const heroCardTitle = document.createElement('h2');
  heroCardTitle.appendChild(createLangElement('span', {
    en: 'Paper facts',
    zh: '论文信息',
  }));

  const heroList = document.createElement('ul');
  (paper.authors || []).forEach((author) => {
    const li = document.createElement('li');
    li.textContent = author;
    heroList.appendChild(li);
  });

  heroCard.appendChild(heroCardTitle);
  heroCard.appendChild(heroList);

  paperHero.appendChild(heroText);
  paperHero.appendChild(heroCard);

  const linkCard = document.createElement('div');
  linkCard.className = 'meta-card';
  const linkTitle = document.createElement('h3');
  linkTitle.appendChild(createLangElement('span', { en: 'Links', zh: '链接' }));
  const linkList = document.createElement('ul');
  linkList.className = 'meta-list';
  Object.entries(paper.links || {}).forEach(([label, url]) => {
    if (!url) return;
    const li = document.createElement('li');
    const a = document.createElement('a');
    a.href = url;
    a.target = '_blank';
    a.rel = 'noreferrer';
    a.textContent = label;
    li.appendChild(a);
    linkList.appendChild(li);
  });
  linkCard.appendChild(linkTitle);
  linkCard.appendChild(linkList);

  const metaCard = document.createElement('div');
  metaCard.className = 'meta-card';
  const metaTitle = document.createElement('h3');
  metaTitle.appendChild(createLangElement('span', { en: 'Metadata', zh: '元信息' }));
  const metaList = document.createElement('ul');
  metaList.className = 'meta-list';
  const metaItems = [
    paper.arxivId ? `arXiv: ${paper.arxivId}` : null,
    paper.date ? `Date: ${paper.date}` : null,
    paper.venue ? `Venue: ${paper.venue}` : null,
  ].filter(Boolean);
  metaItems.forEach((item) => {
    const li = document.createElement('li');
    li.textContent = item;
    metaList.appendChild(li);
  });
  metaCard.appendChild(metaTitle);
  metaCard.appendChild(metaList);

  paperMeta.appendChild(linkCard);
  paperMeta.appendChild(metaCard);

  (paper.sections || []).forEach((section) => {
    const card = document.createElement('div');
    card.className = 'section-card';
    const header = document.createElement('h2');
    header.appendChild(createLangElement('span', section.title));
    card.appendChild(header);

    (section.blocks || []).forEach((block) => {
      card.appendChild(createLevelBlock(block));
    });

    paperSections.appendChild(card);
  });
};

const loadIndex = async () => {
  const response = await fetch('/data/papers.json');
  const data = await response.json();
  state.papersIndex = data.papers;
  renderIndex(state.papersIndex);
};

const loadPaper = async (slug) => {
  const response = await fetch(`/data/papers/${slug}.json`);
  if (!response.ok) {
    throw new Error('Paper not found');
  }
  const paper = await response.json();
  renderPaper(paper);
};

const navigateTo = async (slug) => {
  history.pushState({}, '', slug ? `/${slug}` : '/');
  await route();
};

const route = async () => {
  const slug = getSlug();
  if (!slug) {
    setView('index');
    if (!state.papersIndex) {
      await loadIndex();
    } else {
      renderIndex(state.papersIndex, searchInput.value);
    }
    return;
  }

  setView('paper');
  try {
    await loadPaper(slug);
  } catch (err) {
    setView('index');
    if (!state.papersIndex) {
      await loadIndex();
    }
  }
};

setLang(getInitialLang());
setLevel(getInitialLevel());

langButtons.forEach((btn) => {
  btn.addEventListener('click', () => {
    setLang(btn.dataset.langBtn);
  });
});

levelButtons.forEach((btn) => {
  btn.addEventListener('click', () => {
    setLevel(btn.dataset.levelBtn);
  });
});

if (searchInput) {
  searchInput.addEventListener('input', (event) => {
    if (state.papersIndex) {
      renderIndex(state.papersIndex, event.target.value);
    }
  });
}

if (backBtn) {
  backBtn.addEventListener('click', () => {
    navigateTo('');
  });
}

window.addEventListener('popstate', () => {
  route();
});

route();
