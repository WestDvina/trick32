(() => {
  "use strict";

  const pres = [...document.querySelectorAll(".prose pre")];
  if (!pres.length) return;

  const tip = document.createElement("div");
  tip.className = "copy-tip";
  tip.textContent = "Скопировано";
  document.body.appendChild(tip);

  let timer = null;

  function showTip(el) {
    const r = el.getBoundingClientRect();
    tip.textContent = "Скопировано";
    tip.style.top = `${Math.max(r.top + window.scrollY - 8, 4)}px`;
    tip.style.left = `${r.left + r.width / 2}px`;
    tip.classList.add("is-visible");
    clearTimeout(timer);
    timer = setTimeout(() => tip.classList.remove("is-visible"), 1400);
  }

  async function copy(el) {
    const text = el.querySelector("code")?.innerText ?? el.innerText;
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      const ta = document.createElement("textarea");
      ta.value = text;
      ta.style.position = "fixed";
      ta.style.opacity = "0";
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      ta.remove();
    }
    el.classList.add("copied");
    showTip(el);
    setTimeout(() => el.classList.remove("copied"), 600);
  }

  pres.forEach((pre) => {
    pre.addEventListener("click", () => copy(pre));
  });
})();
