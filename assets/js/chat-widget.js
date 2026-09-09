(() => {
  const API = "https://chat.a62i.ru";
  const LS_SID = "chat_sid_v1";
  const LS_NAME = "chat_name_v1";
  function genSid() {
    return Math.random().toString(36).slice(2, 10) + "-" + Date.now().toString(36);
  }
  function getSid() {
    let s = localStorage.getItem(LS_SID);
    if (!s) { s = genSid(); localStorage.setItem(LS_SID, s); }
    return s;
  }
  function getName() {
    return localStorage.getItem(LS_NAME) || "";
  }
  function setName(v) { localStorage.setItem(LS_NAME, v); }

  const style = document.createElement("style");
  style.textContent = `
.chat-fab{position:fixed;right:18px;bottom:18px;z-index:9999;display:flex;align-items:center;gap:8px;background:#0ea5e9;color:#fff;border:0;border-radius:999px;padding:12px 18px;font:600 14px/1 system-ui,sans-serif;cursor:pointer;box-shadow:0 8px 24px rgba(2,132,199,.35);transition:transform .15s}
.chat-fab:hover{transform:translateY(-1px)}
.chat-fab .dot{width:8px;height:8px;background:#22c55e;border-radius:50%;box-shadow:0 0 0 6px rgba(34,197,94,.15)}
.chat-fab .badge{min-width:18px;height:18px;background:#ef4444;color:#fff;border-radius:999px;font-size:11px;display:grid;place-items:center;padding:0 5px;display:none}
.chat-panel{position:fixed;right:18px;bottom:72px;z-index:9999;width:360px;max-width:calc(100vw - 24px);height:460px;max-height:70vh;background:var(--chat-bg,#fff);border:1px solid #e5e7eb;border-radius:16px;box-shadow:0 16px 40px rgba(0,0,0,.18);display:none;flex-direction:column;overflow:hidden}
.chat-panel.open{display:flex}
@media(max-width:480px){.chat-panel{right:12px;left:12px;width:auto}}
.dark .chat-panel{background:#1f2937;border-color:#374151;color:#e5e7eb}
.chat-head{padding:12px 14px;border-bottom:1px solid #e5e7eb;display:flex;align-items:center;justify-content:space-between;background:#f8fafc}
.dark .chat-head{background:#111827;border-color:#374151}
.chat-head b{font-size:14px}
.chat-head small{color:#64748b;font-size:11px}
.dark .chat-head small{color:#9ca3af}
.chat-close{border:0;background:transparent;font-size:18px;cursor:pointer;color:#64748b}
.chat-body{flex:1;overflow:auto;padding:12px;display:flex;flex-direction:column;gap:8px;background:#fff}
.dark .chat-body{background:#1f2937}
.chat-msg{max-width:78%;padding:8px 10px;border-radius:12px;font-size:13px;line-height:1.4;word-break:break-word}
.chat-msg.user{align-self:flex-end;background:#0ea5e9;color:#fff;border-bottom-right-radius:4px}
.chat-msg.admin{align-self:flex-start;background:#f1f5f9;color:#0f172a;border-bottom-left-radius:4px}
.dark .chat-msg.admin{background:#374151;color:#e5e7eb}
.chat-foot{padding:10px;border-top:1px solid #e5e7eb;display:flex;gap:8px;background:#fff}
.dark .chat-foot{background:#111827;border-color:#374151}
.chat-foot input{flex:1;border:1px solid #e5e7eb;border-radius:999px;padding:8px 12px;font-size:13px;outline:0}
.dark .chat-foot input{background:#1f2937;border-color:#374151;color:#e5e7eb}
.chat-foot button{border:0;background:#0ea5e9;color:#fff;border-radius:999px;padding:8px 14px;font-weight:600;cursor:pointer}
.chat-foot button:disabled{opacity:.5}
.chat-empty{color:#94a3b8;font-size:12px;text-align:center;padding:24px 12px}
`;
  document.head.appendChild(style);

  const fab = document.createElement("button");
  fab.className = "chat-fab";
  fab.innerHTML = '<span class="dot"></span> Написать в чате <span class="badge"></span>';
  document.body.appendChild(fab);

  const panel = document.createElement("div");
  panel.className = "chat-panel";
  panel.innerHTML = `
    <div class="chat-head"><div><b>Чат поддержки</b><br><small>Отвечаю в Telegram — видите здесь</small></div><button class="chat-close">×</button></div>
    <div class="chat-body"><div class="chat-empty">Напишите сообщение — отвечу здесь же.<br>Работаю через HopToDesk / AnyDesk / RuDesktop.</div></div>
    <form class="chat-foot"><input placeholder="Ваше сообщение..." maxlength="2000" autocomplete="off"><button type="submit">Отправить</button></form>
  `;
  document.body.appendChild(panel);
  const body = panel.querySelector(".chat-body");
  const form = panel.querySelector("form");
  const input = form.querySelector("input");
  const badge = fab.querySelector(".badge");
  const closeBtn = panel.querySelector(".chat-close");

  let sid = getSid();
  let lastId = 0;
  let open = false;
  let unread = 0;
  let timer = null;

  function renderMessage(m) {
    const empty = body.querySelector(".chat-empty");
    if (empty) empty.remove();
    const div = document.createElement("div");
    div.className = "chat-msg " + (m.direction === "admin" ? "admin" : "user");
    div.textContent = m.text;
    body.appendChild(div);
  }

  async function poll() {
    try {
      const r = await fetch(`${API}/api/messages?sid=${encodeURIComponent(sid)}&after=${lastId}`);
      if (!r.ok) return;
      const j = await r.json();
      const msgs = j.messages || [];
      let hasNew = false;
      msgs.forEach(m => {
        if (m.id > lastId) {
          renderMessage(m);
          lastId = m.id;
          hasNew = true;
          if (m.direction === "admin" && !open) {
            unread++;
            badge.textContent = unread > 9 ? "9+" : unread;
            badge.style.display = "grid";
          }
        }
      });
      if (hasNew) body.scrollTop = body.scrollHeight;
    } catch {}
  }

  function startPoll() {
    if (timer) clearInterval(timer);
    poll();
    timer = setInterval(poll, 3000);
  }

  fab.addEventListener("click", () => {
    open = !open;
    panel.classList.toggle("open", open);
    if (open) {
      unread = 0; badge.style.display = "none";
      body.scrollTop = body.scrollHeight;
      input.focus();
      startPoll();
    }
  });
  closeBtn.addEventListener("click", () => { open = false; panel.classList.remove("open"); });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const text = input.value.trim();
    if (!text) return;
    input.value = "";
    const btn = form.querySelector("button");
    btn.disabled = true;
    // optimistic
    const tmp = {id: lastId+1, direction:"user", text};
    renderMessage(tmp);
    body.scrollTop = body.scrollHeight;
    try {
      const r = await fetch(`${API}/api/message`, {
        method:"POST",
        headers:{"Content-Type":"application/json"},
        body: JSON.stringify({sid, text, name: getName() || "Гость"})
      });
      if (!r.ok) throw new Error();
      const j = await r.json();
      if (j.id) lastId = Math.max(lastId, j.id);
      // poll immediately
      setTimeout(poll, 500);
    } catch {
      // show error inline
    } finally { btn.disabled = false; }
  });

  // ask name once
  if (!getName()) {
    setTimeout(() => {
      if (!localStorage.getItem(LS_NAME)) {
        const n = prompt("Как к вам обращаться? (необязательно)");
        if (n) setName(n.trim().slice(0,32));
      }
    }, 1500);
  }

  // start polling only when opened to save traffic; but also poll once hidden for badge
  setInterval(() => { if (!open) poll(); }, 8000);
})();
