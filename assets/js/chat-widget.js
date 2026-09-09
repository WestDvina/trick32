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
  function getName() { return localStorage.getItem(LS_NAME) || ""; }
  function setName(v) { localStorage.setItem(LS_NAME, v); }

  const style = document.createElement("style");
  style.textContent = `
.chat-fab{position:fixed;right:16px;bottom:88px;z-index:9998;display:flex;align-items:center;justify-content:center;gap:0;width:52px;height:52px;background:#00c871;color:#fff;border:0;border-radius:50%;cursor:pointer;box-shadow:0 8px 24px rgba(0,172,97,.35);transition:all .22s cubic-bezier(.4,0,.2,1);overflow:hidden}
.chat-fab:hover{width:182px;border-radius:999px;gap:8px;padding:0 14px;right:16px}
.chat-fab .fab-icon{flex-shrink:0;width:22px;height:22px;display:grid;place-items:center}
.chat-fab .fab-icon svg{width:22px;height:22px}
.chat-fab .fab-text{white-space:nowrap;font:600 13px/1 system-ui,sans-serif;opacity:0;max-width:0;overflow:hidden;transition:opacity .18s,max-width .22s}
.chat-fab:hover .fab-text{opacity:1;max-width:120px}
.chat-fab .badge{position:absolute;top:-4px;right:-4px;min-width:18px;height:18px;background:#ef4444;color:#fff;border-radius:999px;font:700 11px/18px system-ui,sans-serif;display:none;place-items:center;padding:0 5px;box-shadow:0 2px 6px rgba(0,0,0,.2)}
.chat-fab .dot{position:absolute;bottom:2px;right:2px;width:10px;height:10px;background:#fff;border:2px solid #00c871;border-radius:50%}
.chat-panel{position:fixed;right:16px;bottom:88px;z-index:9999;width:380px;max-width:calc(100vw - 24px);height:480px;max-height:72vh;background:#fff;border:1px solid #e5e7eb;border-radius:16px;box-shadow:0 16px 40px rgba(0,0,0,.18);display:none;flex-direction:column;overflow:hidden}
.chat-panel.open{display:flex}
.chat-head{padding:12px 14px;border-bottom:1px solid #e5e7eb;display:flex;align-items:center;justify-content:space-between;background:#f0fdf4;flex-shrink:0}
.chat-head b{font-size:14px;color:#064e3b}
.chat-head small{color:#065f46;font-size:11px}
.chat-close{width:28px;height:28px;border:0;background:#fff;border-radius:50%;display:grid;place-items:center;font-size:14px;line-height:1;cursor:pointer;color:#065f46;box-shadow:0 1px 4px rgba(0,0,0,.08);flex-shrink:0}
.chat-close:hover{background:#e5e7eb}
.chat-body{flex:1;overflow:auto;padding:12px;display:flex;flex-direction:column;gap:8px;background:#fff;overscroll-behavior:contain}
.chat-msg{max-width:78%;padding:8px 11px;border-radius:12px;font-size:13px;line-height:1.45;word-break:break-word}
.chat-msg.user{align-self:flex-end;background:#00c871;color:#fff;border-bottom-right-radius:4px}
.chat-msg.admin{align-self:flex-start;background:#e8fff4;color:#064e3b;border:1px solid #aaf2d7;border-bottom-left-radius:4px}
.chat-foot{padding:10px;border-top:1px solid #e5e7eb;display:flex;gap:8px;background:#fff;flex-shrink:0}
.chat-foot input{flex:1;border:1px solid #e5e7eb;border-radius:999px;padding:9px 14px;font-size:13px;outline:0;background:#fff}
.chat-foot input:focus{border-color:#00c871;box-shadow:0 0 0 3px rgba(0,224,127,.15)}
.chat-foot button{border:0;background:#00c871;color:#fff;border-radius:999px;padding:9px 16px;font:700 13px system-ui,sans-serif;cursor:pointer;flex-shrink:0}
.chat-foot button:hover{background:#00a86a}
.chat-foot button:disabled{opacity:.5}
.chat-empty{color:#94a3b8;font-size:12px;text-align:center;padding:28px 12px;line-height:1.5}
.chat-gate{margin:auto;display:flex;flex-direction:column;gap:10px;align-items:center;justify-content:center;padding:24px 16px;text-align:center;max-width:280px}
.chat-gate b{font-size:15px;color:#064e3b}
.chat-gate p{font-size:13px;color:#475569;margin:0}
.chat-gate input{width:100%;border:1px solid #e5e7eb;border-radius:999px;padding:9px 14px;font-size:13px;outline:0;text-align:center}
.chat-gate input:focus{border-color:#00c871;box-shadow:0 0 0 3px rgba(0,224,127,.15)}
.chat-gate .gate-btn{width:100%;border:0;background:#00c871;color:#fff;border-radius:999px;padding:10px;font:700 13px system-ui,sans-serif;cursor:pointer}
.chat-gate .gate-btn:hover{background:#00a86a}
.chat-gate small{font-size:11px;color:#94a3b8}
.dark .chat-panel{background:#1f2937;border-color:#374151}
.dark .chat-head{background:#064e3b;border-color:#374151}
.dark .chat-head b{color:#ecfdf5}
.dark .chat-head small{color:#a7f3d0}
.dark .chat-close{background:#1f2937;color:#a7f3d0}
.dark .chat-body{background:#1f2937}
.dark .chat-msg.admin{background:#064e3b;color:#ecfdf5;border-color:#047857}
.dark .chat-foot{background:#111827;border-color:#374151}
.dark .chat-foot input{background:#1f2937;border-color:#374151;color:#e5e7eb}
.dark .chat-gate b{color:#ecfdf5}
.dark .chat-gate p{color:#9ca3af}
/* mobile fullscreen */
@media(max-width:640px){
  .chat-panel{right:0;left:0;top:0;bottom:0;width:auto;height:100dvh;max-height:100dvh;max-width:none;border-radius:0;border:0}
  .chat-fab{right:14px;bottom:72px;width:48px;height:48px}
  .chat-fab:hover{width:48px;border-radius:50%}
  .chat-fab:hover .fab-text{opacity:0;max-width:0}
  .chat-fab .fab-text{display:none}
  body.chat-open{overflow:hidden}
}
`;
  document.head.appendChild(style);

  const fab = document.createElement("button");
  fab.className = "chat-fab";
  fab.setAttribute("aria-label", "Написать в чате");
  fab.innerHTML = '<span class="fab-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg></span><span class="fab-text">Написать в чате</span><span class="dot"></span><span class="badge"></span>';
  document.body.appendChild(fab);

  const panel = document.createElement("div");
  panel.className = "chat-panel";
  panel.innerHTML = `
    <div class="chat-head"><div><b>Чат поддержки</b><br><small>Отвечаю в Telegram — видите здесь</small></div><button class="chat-close" aria-label="Закрыть">✕</button></div>
    <div class="chat-body"><div class="chat-empty">Напишите сообщение — отвечу здесь же.<br>Работаю через HopToDesk / AnyDesk / RuDesktop.</div></div>
    <form class="chat-foot"><input type="text" style="position:absolute;left:-9999px;top:-9999px" tabindex="-1" autocomplete="off" name="hp"><input placeholder="Ваше сообщение..." maxlength="2000" autocomplete="off" name="msg"><button type="submit">Отправить</button></form>
  `;
  document.body.appendChild(panel);
  const body = panel.querySelector(".chat-body");
  const form = panel.querySelector("form");
  const input = form.querySelector('input[name="msg"]');
  const hpInput = form.querySelector('input[name="hp"]');
  const badge = fab.querySelector(".badge");
  const closeBtn = panel.querySelector(".chat-close");

  let sid = getSid();
  const LS_LAST = "chat_last_" + sid;
  let lastId = parseInt(localStorage.getItem(LS_LAST) || "0", 10) || 0;
  let open = false;
  let unread = 0;
  let timer = null;
  let gateShown = false;
  let firstPoll = true;

  function renderMessage(m) {
    const empty = body.querySelector(".chat-empty");
    if (empty) empty.remove();
    const div = document.createElement("div");
    div.className = "chat-msg " + (m.direction === "admin" ? "admin" : "user");
    div.textContent = m.text;
    body.appendChild(div);
  }

  function showGate() {
    if (gateShown || getName()) return;
    gateShown = true;
    const empty = body.querySelector(".chat-empty");
    if (empty) empty.style.display = "none";
    const gate = document.createElement("div");
    gate.className = "chat-gate";
    gate.innerHTML = '<b>Как к вам обращаться?</b><p>Введите имя — нужно для ответа</p><input class="gate-input" placeholder="Ваше имя" maxlength="32" autocomplete="name"><button class="gate-btn" type="button">Продолжить</button><small>Защита от спама включена</small>';
    body.appendChild(gate);
    const gateInput = gate.querySelector(".gate-input");
    const gateBtn = gate.querySelector(".gate-btn");
    setTimeout(() => gateInput.focus(), 100);
    function submitGate() {
      const v = gateInput.value.trim().slice(0,32);
      if (!v) { gateInput.style.borderColor="#ef4444"; gateInput.focus(); return; }
      setName(v);
      gate.remove();
      const e = body.querySelector(".chat-empty");
      if (e) e.style.display = "";
      input.focus();
    }
    gateBtn.addEventListener("click", submitGate);
    gateInput.addEventListener("keydown", e => { if (e.key === "Enter") { e.preventDefault(); submitGate(); }});
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
          const gate = body.querySelector(".chat-gate");
          if (gate) gate.remove();
          renderMessage(m);
          lastId = m.id;
          localStorage.setItem(LS_LAST, String(lastId));
          hasNew = true;
          if (!firstPoll && m.direction === "admin" && !open) {
            unread++;
            badge.textContent = unread > 9 ? "9+" : unread;
            badge.style.display = "grid";
          }
        }
      });
      if (firstPoll) firstPoll = false;
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
    document.body.classList.toggle("chat-open", open && window.innerWidth <= 640);
    if (open) {
      unread = 0; badge.style.display = "none";
      localStorage.setItem(LS_LAST, String(lastId));
      if (!getName()) showGate();
      else {
        const empty = body.querySelector(".chat-empty");
        if (empty) empty.style.display = "";
      }
      body.scrollTop = body.scrollHeight;
      const gateInput = body.querySelector(".gate-input");
      if (gateInput) gateInput.focus(); else input.focus();
      startPoll();
    } else {
      document.body.classList.remove("chat-open");
    }
  });
  closeBtn.addEventListener("click", () => { open = false; panel.classList.remove("open"); document.body.classList.remove("chat-open"); });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (hpInput.value.trim() !== "") return; // honeypot
    if (!getName()) { showGate(); return; }
    const text = input.value.trim();
    if (!text) return;
    input.value = "";
    const btn = form.querySelector('button[type="submit"]');
    btn.disabled = true;
    setTimeout(() => btn.disabled = false, 1000); // anti-spam throttle
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
      setTimeout(poll, 500);
    } catch {}
    finally { btn.disabled = false; }
  });

  setInterval(() => { if (!open) poll(); }, 8000);
})();
