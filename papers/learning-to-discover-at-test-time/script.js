const langButtons = document.querySelectorAll('[data-lang-btn]');
const levelButtons = document.querySelectorAll('[data-level-btn]');

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
