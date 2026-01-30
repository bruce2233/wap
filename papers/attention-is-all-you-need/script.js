const copyButtons = document.querySelectorAll("[data-copy], [data-copy-target]");

copyButtons.forEach((button) => {
  button.addEventListener("click", async () => {
    const directText = button.getAttribute("data-copy");
    const targetId = button.getAttribute("data-copy-target");
    let text = directText;

    if (!text && targetId) {
      const target = document.getElementById(targetId);
      if (target) {
        text = target.textContent.trim();
      }
    }

    if (!text) return;

    try {
      await navigator.clipboard.writeText(text);
      const original = button.textContent;
      button.textContent = "Copied";
      setTimeout(() => {
        button.textContent = original;
      }, 1400);
    } catch (err) {
      button.textContent = "Copy failed";
    }
  });
});

const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
const revealElements = document.querySelectorAll(".reveal");

if (prefersReducedMotion) {
  revealElements.forEach((el) => el.classList.add("is-visible"));
} else {
  const revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
        }
      });
    },
    { threshold: 0.18 }
  );

  revealElements.forEach((el) => revealObserver.observe(el));
}

const navLinks = Array.from(document.querySelectorAll(".section-nav a"));
const sections = Array.from(document.querySelectorAll("section[data-section]"));
const linkById = new Map();

navLinks.forEach((link) => {
  const href = link.getAttribute("href") || "";
  if (href.startsWith("#")) {
    linkById.set(href.slice(1), link);
  }
});

if (navLinks.length && sections.length) {
  const navObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const active = linkById.get(entry.target.id);
        if (!active) return;
        navLinks.forEach((link) => link.classList.remove("active"));
        active.classList.add("active");
      });
    },
    { threshold: 0.4, rootMargin: "0px 0px -40% 0px" }
  );

  sections.forEach((section) => navObserver.observe(section));
}
