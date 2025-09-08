from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from starlette.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routers.todos import router as todos_router
from app.middlewares.request_id import RequestIdMiddleware
from app.middlewares.security_headers import SecurityHeadersMiddleware

app = FastAPI(title="TODO SaaS Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add basic middlewares for observability and security
app.add_middleware(RequestIdMiddleware)
app.add_middleware(SecurityHeadersMiddleware)


@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.app_env}


@app.get("/", response_class=HTMLResponse)
async def index():
    return """
<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>Todos</title>
  <style>
    :root { --bg:#0b1117; --card:#111827; --muted:#9aa4b2; --text:#e5e7eb; --accent:#22d3ee; --ok:#10b981; --warn:#f59e0b; }
    * { box-sizing: border-box; }
    body { margin: 0; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, Helvetica Neue, Arial, \"Apple Color Emoji\", \"Segoe UI Emoji\"; background: var(--bg); color: var(--text); }
    header { padding: 24px; display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #1f2937; }
    header h1 { margin: 0; font-size: 20px; font-weight: 600; letter-spacing: .2px; }
    .controls { display: flex; gap: 12px; align-items: center; }
    select, input, button { background: #0f172a; color: var(--text); border: 1px solid #1f2937; border-radius: 8px; padding: 8px 10px; }
    button.primary { background: #0ea5e9; border-color: #0284c7; color: white; }
    main { padding: 24px; }
    .grid { display: grid; gap: 16px; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); }
    .card { background: var(--card); border: 1px solid #1f2937; border-radius: 12px; padding: 16px; display: flex; flex-direction: column; gap: 8px; box-shadow: 0 8px 24px rgba(0,0,0,.25); }
    .title { font-weight: 600; font-size: 16px; }
    .desc { color: var(--muted); font-size: 14px; min-height: 18px; }
    .meta { display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: var(--muted); }
    .badge { display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 12px; border: 1px solid #1f2937; }
    .badge.ok { color: var(--ok); border-color: #065f46; background: rgba(16,185,129,.07); }
    .badge.warn { color: var(--warn); border-color: #854d0e; background: rgba(245,158,11,.07); }
    .actions { display: flex; gap: 8px; margin-top: 6px; }
    .actions button { cursor: pointer; }
    .toolbar { display:flex; gap:12px; align-items:center; }
    .empty { color: var(--muted); padding: 24px; text-align: center; }
    form.new { display:flex; gap:8px; }
    form.new input[type=\"text\"]{ flex:1; }
    .row { display:flex; align-items:center; gap:8px; }
    .row.space { justify-content: space-between; }
    .menu { position: relative; margin-left: auto; }
    .menu-btn { background: transparent; border: none; color: var(--muted); font-size: 18px; line-height: 1; cursor: pointer; padding: 4px 6px; border-radius: 6px; }
    .menu-btn:hover { background: #0f172a; color: var(--text); }
    .menu-list { position: absolute; top: 28px; right: 0; background: #0f172a; border: 1px solid #1f2937; border-radius: 10px; min-width: 160px; display: none; box-shadow: 0 10px 24px rgba(0,0,0,.35); z-index: 20; }
    .menu-list.visible { display: block; }
    .menu-item { padding: 10px 12px; font-size: 14px; color: var(--text); cursor: pointer; }
    .menu-item:hover { background: #111827; }
  </style>
  <script>
    async function api(path, opts){
      const res = await fetch(path, { headers: { 'Content-Type': 'application/json' }, ...opts });
      if(!res.ok){ throw new Error('HTTP '+res.status); }
      return res.headers.get('content-type')?.includes('application/json') ? res.json() : res.text();
    }
    function fmtDate(iso){ try{ return new Date(iso).toLocaleString(); }catch(e){ return iso } }
    function closeAllMenus(){
      document.querySelectorAll('.menu-list.visible').forEach(el => el.classList.remove('visible'));
    }
    function toggleMenu(id){
      const el = document.getElementById('menu-'+id);
      if(!el) return; const vis = el.classList.contains('visible');
      closeAllMenus(); if(!vis) el.classList.add('visible');
    }
    async function editTodo(id, title, desc){
      try{
        const nt = prompt('New title', title ?? ''); if(nt === null) return;
        const nd = prompt('New description (optional)', desc ?? ''); if(nd === null) return;
        const body = { title: nt.trim(), description: (nd||'').trim() || null };
        await api('/todos/'+id, { method:'PUT', body: JSON.stringify(body) });
        closeAllMenus();
        load();
      }catch(e){ console.error(e); }
    }
    async function load(){
      const sel = document.getElementById('filter');
      const lim = document.getElementById('limit');
      const qs = new URLSearchParams();
      if(sel.value !== 'all'){ qs.set('completed', sel.value==='true'); }
      qs.set('limit', lim.value || '20');
      const data = await api('/todos/paged?'+qs.toString());
      const list = data.items || [];
      const grid = document.getElementById('grid');
      grid.innerHTML = '';
      if(!list.length){ grid.innerHTML = '<div class=\"empty\">No todos yet</div>'; return }
      for(const t of list){
        const el = document.createElement('div'); el.className = 'card';
        const safeTitle = JSON.stringify(t.title ?? '');
        const safeDesc = JSON.stringify(t.description ?? null);
        el.innerHTML = `
          <div class=\"row space\">
            <div class=\"title\">${t.title}</div>
            <div class=\"menu\">
              <button class=\"menu-btn\" onclick=\"toggleMenu('${t.id}')\" aria-label=\"More\">⋯</button>
              <div id=\"menu-${t.id}\" class=\"menu-list\">
                <div class=\"menu-item\" onclick=\"editTodo('${t.id}', ${safeTitle}, ${safeDesc})\">Edit</div>
                <div class=\"menu-item\" onclick=\"delTodo('${t.id}')\">Delete</div>
              </div>
            </div>
          </div>
          <div class=\"desc\">${t.description ?? ''}</div>
          <div class=\"meta\">
            <span>${fmtDate(t.created_at)}</span>
            <span class=\"badge ${t.completed?'ok':'warn'}\">${t.completed?'Done':'Pending'}</span>
          </div>
          <div class=\"actions\">
            <button onclick=\"toggle('${t.id}', ${!t.completed})\">${t.completed?'Mark pending':'Mark done'}</button>
          </div>`;
        grid.appendChild(el);
      }
    }
    async function toggle(id, status){
      await api('/todos/'+id,{method:'PUT', body: JSON.stringify({completed: status})});
      load();
    }
    async function delTodo(id){ await api('/todos/'+id,{method:'DELETE'}); load(); }
    async function createTodo(ev){ ev.preventDefault();
      const title = document.getElementById('title').value.trim();
      const desc = document.getElementById('desc').value.trim() || null;
      if(!title) return;
      await api('/todos/', {method:'POST', body: JSON.stringify({title, description: desc, completed:false})});
      document.getElementById('title').value = '';
      document.getElementById('desc').value = '';
      load();
    }
    window.addEventListener('DOMContentLoaded', () => {
      load();
      document.addEventListener('click', (e)=>{
        if(!(e.target.closest && e.target.closest('.menu'))){ closeAllMenus(); }
      });
      document.getElementById('refresh').onclick = load;
      document.getElementById('filter').onchange = load;
      document.getElementById('limit').onchange = load;
      document.getElementById('new').addEventListener('submit', createTodo);
    });
  </script>
</head>
<body>
  <header>
    <h1>Todos</h1>
    <div class=\"toolbar\">
      <div class=\"controls\">
        <label>Completed</label>
        <select id=\"filter\">
          <option value=\"all\">All</option>
          <option value=\"true\">Only done</option>
          <option value=\"false\">Only pending</option>
        </select>
        <label>Limit</label>
        <select id=\"limit\">
          <option>10</option>
          <option selected>20</option>
          <option>50</option>
        </select>
        <button id=\"refresh\">Refresh</button>
      </div>
      <form id=\"new\" class=\"new\">
        <input id=\"title\" type=\"text\" placeholder=\"Title\" />
        <input id=\"desc\" type=\"text\" placeholder=\"Description (optional)\" />
        <button class=\"primary\" type=\"submit\">Create</button>
      </form>
    </div>
  </header>
  <main>
    <div id=\"grid\" class=\"grid\"></div>
  </main>
</body>
</html>
    """


app.include_router(todos_router)
