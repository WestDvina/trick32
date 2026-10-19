// Site override of themes/congo/assets/js/code.js (theme is a git submodule).
// Icon-only copy button for article code blocks: no text label, checkmark after copying.
(() => {
  "use strict";

  const bundle = document.getElementById("script-bundle");
  const labelCopy = (bundle && bundle.getAttribute("data-copy")) || "Копировать";
  const labelDone = (bundle && bundle.getAttribute("data-copied")) || "Скопировано";

  const ICON_COPY =
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="9" width="12" height="12" rx="2.5"/><path d="M5 15H4.5A2.5 2.5 0 0 1 2 12.5v-8A2.5 2.5 0 0 1 4.5 2h8A2.5 2.5 0 0 1 15 4.5V5"/></svg>';
  const ICON_DONE =
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6L9 17l-5-5"/></svg>';

  function fallbackCopy(text) {
    const ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.className = "copy-textarea";
    document.body.appendChild(ta);
    ta.select();
    ta.setSelectionRange(0, 999999);
    try {
      document.execCommand("copy");
    } catch (_) {}
    ta.remove();
  }

  function markCopied(button) {
    button.innerHTML = ICON_DONE;
    button.classList.add("is-copied");
    button.setAttribute("aria-label", labelDone);
    clearTimeout(button._copyTimer);
    button._copyTimer = setTimeout(() => {
      button.innerHTML = ICON_COPY;
      button.classList.remove("is-copied");
      button.setAttribute("aria-label", labelCopy);
    }, 1600);
  }

  async function copyCode(button, highlight) {
    const codeEl = highlight.querySelector("pre code") || highlight.querySelector("pre");
    const text = codeEl ? codeEl.innerText : "";
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(text);
      } else {
        fallbackCopy(text);
      }
    } catch (_) {
      fallbackCopy(text);
    }
    markCopied(button);
  }

  function addCopyButton(highlight) {
    const button = document.createElement("button");
    button.className = "copy-button";
    button.type = "button";
    button.setAttribute("aria-label", labelCopy);
    button.title = labelCopy;
    button.innerHTML = ICON_COPY;
    button.addEventListener("click", (e) => {
      e.preventDefault();
      e.stopPropagation();
      copyCode(button, highlight);
    });
    highlight.insertBefore(button, highlight.firstChild);

    if (!highlight.parentNode.classList.contains("highlight-wrapper")) {
      const wrapper = document.createElement("div");
      wrapper.className = "highlight-wrapper";
      highlight.parentNode.insertBefore(wrapper, highlight);
      wrapper.appendChild(highlight);
    }
  }

  window.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".highlight").forEach(addCopyButton);
  });
})();
