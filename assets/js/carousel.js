(() => {
  "use strict";

  const carousels = [...document.querySelectorAll("[data-carousel]")];
  if (!carousels.length) return;

  const isMobile = () => window.matchMedia("(max-width: 767px)").matches;

  carousels.forEach((root) => {
    const track = root.querySelector("[data-carousel-track]");
    const slides = [...track.children];
    const prev = root.querySelector("[data-carousel-prev]");
    const next = root.querySelector("[data-carousel-next]");
    if (slides.length < 2) {
      prev.remove();
      next.remove();
      return;
    }

    const perView = () => (isMobile() ? 1 : 3);
    const maxIndex = () => Math.max(0, slides.length - perView());
    let index = 0;

    function update() {
      index = Math.min(index, maxIndex());
      const shift = isMobile()
        ? index * 100
        : index * (100 / 3);
      track.style.transform = `translateX(-${shift}%)`;
      prev.hidden = index === 0;
      next.hidden = index >= maxIndex();
    }

    prev.addEventListener("click", () => {
      index = Math.max(0, index - 1);
      update();
    });
    next.addEventListener("click", () => {
      index = Math.min(maxIndex(), index + 1);
      update();
    });

    document.addEventListener("keydown", (e) => {
      if (e.key !== "ArrowLeft" && e.key !== "ArrowRight") return;
      if (!root.closest("article")) return;
      if (e.target.closest("input, textarea")) return;
      if (e.key === "ArrowLeft") {
        index = Math.max(0, index - 1);
      } else {
        index = Math.min(maxIndex(), index + 1);
      }
      update();
    });

    let tx = 0;
    root.addEventListener(
      "touchstart",
      (e) => (tx = e.touches[0].clientX),
      { passive: true }
    );
    root.addEventListener(
      "touchend",
      (e) => {
        const dx = e.changedTouches[0].clientX - tx;
        if (Math.abs(dx) > 40) {
          if (dx < 0) index = Math.min(maxIndex(), index + 1);
          else index = Math.max(0, index - 1);
          update();
        }
      },
      { passive: true }
    );

    window.addEventListener("resize", update);
    update();
  });
})();