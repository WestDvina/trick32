(() => {
  "use strict";

  const figures = [...document.querySelectorAll("figure[data-lightbox]")];
  if (!figures.length) return;

  const node = document.createElement("div");
  node.className = "lightbox";
  node.innerHTML = `
    <button class="lightbox__close" type="button" aria-label="Закрыть">✕</button>
    <button class="lightbox__prev" type="button" aria-label="Назад">‹</button>
    <div class="lightbox__stage"><img alt="" /></div>
    <button class="lightbox__next" type="button" aria-label="Вперёд">›</button>
    <div class="lightbox__counter" role="status"></div>
  `;
  const img = node.querySelector(".lightbox__stage img");
  const counter = node.querySelector(".lightbox__counter");
  const closeBtn = node.querySelector(".lightbox__close");
  const prevBtn = node.querySelector(".lightbox__prev");
  const nextBtn = node.querySelector(".lightbox__next");

  let items = [];
  let index = 0;

  function show() {
    const item = items[index];
    img.alt = item.alt || "";
    img.src = item.src;
    counter.textContent = `${index + 1} / ${items.length}`;
  }

  function open(fig) {
    items = figures.map((f) => ({
      src: figFor(f),
      alt: f.querySelector("img")?.alt || "",
    }));
    index = figures.indexOf(fig);
    node.classList.add("is-open");
    document.body.appendChild(node);
    document.body.style.overflow = "hidden";
    show();
  }

  function close() {
    node.classList.remove("is-open");
    document.body.removeChild(node);
    document.body.style.overflow = "";
  }

  function step(d) {
    index = (index + d + items.length) % items.length;
    show();
  }

  function figFor(f) {
    const s = f.getAttribute("data-src");
    if (s) return s;
    const im = f.querySelector("img");
    return im ? im.currentSrc || im.src : null;
  }

  document.addEventListener("click", (e) => {
    const fig = e.target.closest("figure[data-lightbox]");
    if (!fig) return;
    e.preventDefault();
    open(fig);
  });

  closeBtn.addEventListener("click", close);
  prevBtn.addEventListener("click", () => step(-1));
  nextBtn.addEventListener("click", () => step(1));
  node.addEventListener("click", (e) => {
    if (e.target === node || e.target === node.querySelector(".lightbox__stage")) close();
  });

  document.addEventListener("keydown", (e) => {
    if (!node.classList.contains("is-open")) return;
    if (e.key === "Escape") close();
    if (e.key === "ArrowLeft") step(-1);
    if (e.key === "ArrowRight") step(1);
  });

  let tx = 0;
  node.addEventListener("touchstart", (e) => { tx = e.touches[0].clientX; }, { passive: true });
  node.addEventListener("touchend", (e) => {
    const dx = e.changedTouches[0].clientX - tx;
    if (Math.abs(dx) > 40) step(dx < 0 ? 1 : -1);
  }, { passive: true });
})();