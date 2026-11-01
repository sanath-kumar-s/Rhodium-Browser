"""`rhodium://downloads` internal page.

Pure presentational page. It renders a JSON snapshot supplied by the Python
DownloadManager and forwards user actions back through `rhodium://` routes.
Python remains the single source of truth for download state; this page has
no independent download management logic.
"""

from rhodium.theme import css_vars


def get_downloads_page_html(downloads_json: str = "[]") -> str:
    safe_json = (downloads_json or "[]").replace("</", "<\\/")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Downloads — Rhodium</title>
<style>
{css_vars()}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
    background: var(--bg_app); color: var(--text_primary);
    font-family: "Segoe UI", Inter, -apple-system, BlinkMacSystemFont, sans-serif;
    min-height: 100vh;
}}
.page {{ max-width: 960px; margin: 0 auto; padding: 36px 24px 56px; }}
.header {{
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 26px; gap: 16px; flex-wrap: wrap;
}}
.heading {{ display: flex; align-items: center; gap: 14px; }}
.heading-icon {{
    width: 44px; height: 44px; border-radius: 13px;
    background: var(--accent_soft); color: var(--accent);
    display: grid; place-items: center;
}}
.heading-icon svg {{ width: 22px; height: 22px; }}
.heading h1 {{ font-size: 22px; font-weight: 700; letter-spacing: -.02em; }}
.heading .sub {{ font-size: 12px; color: var(--text_muted); margin-top: 2px; }}
.header-actions {{ display: flex; gap: 10px; align-items: center; flex: 1; justify-content: flex-end; }}
.search {{
    background: var(--bg_surface); border: 1px solid var(--border_strong); border-radius: 10px;
    color: var(--text_primary); padding: 9px 14px; font-size: 13px; width: min(280px, 100%);
    outline: none; transition: border-color .15s, box-shadow .15s;
}}
.search:focus {{ border-color: var(--accent); box-shadow: 0 0 0 3px var(--accent_soft); }}
.btn {{
    background: var(--bg_surface); color: var(--text_secondary); border: 1px solid var(--border_strong);
    border-radius: 10px; padding: 9px 14px; font-size: 12px; cursor: pointer;
    transition: background .15s, color .15s, border-color .15s;
}}
.btn:hover {{ background: var(--bg_hover); color: var(--text_primary); }}
.btn-danger {{ color: var(--danger); }}
.btn-danger:hover {{ background: var(--danger_soft); border-color: var(--danger); color: var(--danger); }}
.section {{ margin-bottom: 30px; }}
.section-title {{
    display: flex; align-items: center; gap: 8px;
    font-size: 11px; font-weight: 700; letter-spacing: .1em;
    text-transform: uppercase; color: var(--text_muted); margin-bottom: 12px;
}}
.section-title .count {{
    color: var(--text_muted); font-weight: 600; opacity: .7;
}}
.list {{ display: flex; flex-direction: column; gap: 8px; }}
.item {{
    background: var(--bg_surface); border: 1px solid var(--border); border-radius: 14px;
    padding: 14px 16px; display: grid; grid-template-columns: 42px 1fr auto;
    gap: 14px; align-items: start; transition: border-color .15s, box-shadow .15s;
}}
.item:hover {{ border-color: var(--border_strong); box-shadow: var(--shadow_sm); }}
.item.executable {{ border-left: 3px solid var(--warning); }}
.icon {{
    width: 40px; height: 40px; border-radius: 12px;
    background: var(--bg_sunken); display: grid; place-items: center; font-size: 18px;
}}
.meta {{ min-width: 0; }}
.name {{
    font-size: 13px; font-weight: 600; color: var(--text_primary);
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}}
.status {{ font-size: 11px; color: var(--text_secondary); margin-top: 3px; }}
.status .err {{ color: var(--danger); }}
.details {{ font-size: 11px; color: var(--text_muted); margin-top: 4px; word-break: break-all; }}
.progress-wrap {{ margin-top: 9px; }}
.progress {{
    height: 5px; background: var(--bg_sunken); border-radius: 3px; overflow: hidden;
}}
.progress-bar {{
    height: 100%; background: linear-gradient(90deg, var(--accent), #8B6FE0); border-radius: 3px;
    transition: width .2s ease;
}}
.progress-text {{ font-size: 10px; color: var(--text_muted); margin-top: 5px; }}
.actions {{ display: flex; gap: 6px; flex-wrap: wrap; justify-content: flex-end; }}
.action {{
    background: var(--bg_sunken); color: var(--text_secondary); border: none; border-radius: 8px;
    padding: 6px 11px; font-size: 11px; cursor: pointer; transition: background .15s, color .15s;
}}
.action:hover {{ background: var(--bg_active); color: var(--text_primary); }}
.action.primary {{ background: var(--accent_soft); color: var(--accent); font-weight: 600; }}
.action.primary:hover {{ background: var(--accent_soft_hover); color: var(--accent_hover); }}
.action.danger {{ color: var(--danger); }}
.action.danger:hover {{ background: var(--danger_soft); color: var(--danger); }}
.empty {{
    text-align: center; color: var(--text_muted); padding: 48px 20px; font-size: 13px;
}}
.empty .big {{ font-size: 42px; opacity: .5; margin-bottom: 12px; }}
</style>
</head>
<body>
<div class="page">
    <div class="header">
        <div class="heading">
            <div class="heading-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"
                     stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12"/><path d="m7 10 5 5 5-5"/><path d="M4 19h16"/></svg>
            </div>
            <div>
                <h1>Downloads</h1>
                <div class="sub">Files you've downloaded with Rhodium</div>
            </div>
        </div>
        <div class="header-actions">
            <input type="search" class="search" id="search" placeholder="Search downloads…">
            <button class="btn btn-danger" id="clear-btn">Clear</button>
        </div>
    </div>

    <div id="sections"></div>

    <div class="empty" id="empty-msg" style="display:none">
        <div class="big">⬇️</div>
        <div>No downloads yet</div>
    </div>
</div>
<script>
const ALL_DOWNLOADS = {safe_json};

function esc(s) {{
    return String(s == null ? '' : s)
        .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
        .replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}}

function fmtBytes(v) {{
    if (v == null || v < 0) return 'Unknown';
    const u = ['B','KB','MB','GB','TB'];
    let s = Number(v);
    for (const unit of u) {{
        if (s < 1024) return unit === 'B' ? Math.round(s)+' '+unit : s.toFixed(1)+' '+unit;
        s /= 1024;
    }}
    return s.toFixed(1)+' PB';
}}

function fmtStatus(d) {{
    const s = (d.status || '').toUpperCase();
    if (s === 'COMPLETED' && d.total_size > 0) return 'Completed — '+fmtBytes(d.total_size);
    const map = {{
        QUEUED:'Starting…', DOWNLOADING:'Downloading…', PAUSED:'Paused',
        COMPLETED:'Completed', FAILED:'Failed', CANCELLED:'Cancelled', INTERRUPTED:'Interrupted'
    }};
    return map[s] || s;
}}

function fmtEta(sec) {{
    if (sec == null || sec < 0) return '';
    if (sec < 60) return sec + ' sec left';
    const m = Math.floor(sec / 60);
    if (m < 60) return m + ' min left';
    return Math.floor(m / 60) + ' hr ' + (m % 60) + ' min left';
}}

function iconFor(name) {{
    const n = (name || '').toLowerCase();
    if (/\.(exe|msi|msix|msp|bat|cmd|ps1|scr|jar)$/.test(n)) return '⚙️';
    if (/\.(zip|rar|7z|tar|gz|bz2|xz|iso)$/.test(n)) return '📦';
    if (/\.pdf$/.test(n)) return '📕';
    if (/\.(mp3|wav|flac|ogg|m4a)$/.test(n)) return '🎵';
    if (/\.(mp4|mkv|avi|mov|webm)$/.test(n)) return '🎬';
    if (/\.(jpg|jpeg|png|gif|webp|bmp|svg)$/.test(n)) return '🖼️';
    if (/\.(doc|docx|txt|rtf|odt)$/.test(n)) return '📝';
    if (/\.(xls|xlsx|csv|ods)$/.test(n)) return '📊';
    if (/\.(ppt|pptx|odp)$/.test(n)) return '📽️';
    if (/\.(py|js|html|css|json|xml|ts)$/.test(n)) return '📜';
    return '📄';
}}

function actionUrl(id, action) {{
    return 'rhodium://download-action?id=' + id + '&action=' + action;
}}

function renderItem(d) {{
    const s = (d.status || '').toUpperCase();
    const active = ['QUEUED','DOWNLOADING','PAUSED'].includes(s);
    const isCompleted = s === 'COMPLETED';
    const isFailed = ['FAILED','CANCELLED','INTERRUPTED'].includes(s);

    let actions = '';
    if (isCompleted) {{
        actions += '<button class="action primary" data-href="'+actionUrl(d.id,'open')+'">Open</button>';
        actions += '<button class="action" data-href="'+actionUrl(d.id,'folder')+'">Show in folder</button>';
        actions += '<button class="action danger" data-href="'+actionUrl(d.id,'delete')+'">Delete file</button>';
        actions += '<button class="action" data-href="'+actionUrl(d.id,'remove')+'">Remove</button>';
    }} else if (isFailed) {{
        if (d.can_retry) actions += '<button class="action primary" data-href="'+actionUrl(d.id,'retry')+'">Retry</button>';
        actions += '<button class="action" data-href="'+actionUrl(d.id,'remove')+'">Remove</button>';
    }} else if (active) {{
        if (d.can_resume)
            actions += '<button class="action primary" data-href="'+actionUrl(d.id,'resume')+'">Resume</button>';
        else if (d.can_pause)
            actions += '<button class="action" data-href="'+actionUrl(d.id,'pause')+'">Pause</button>';
        actions += '<button class="action danger" data-href="'+actionUrl(d.id,'cancel')+'">Cancel</button>';
    }}

    let progress = '';
    if (active) {{
        const pct = d.total_size > 0 ? Math.min(100, Math.round(d.downloaded_size*100/d.total_size)) : 0;
        let progText = d.total_size > 0
            ? fmtBytes(d.downloaded_size)+' / '+fmtBytes(d.total_size)+' · '+pct+'%'
            : fmtBytes(d.downloaded_size)+' · Downloading…';
        if (d.speed > 0) progText += ' · ' + fmtBytes(d.speed) + '/s';
        if (d.eta >= 0) progText += ' · ' + fmtEta(d.eta);
        progress = '<div class="progress-wrap"><div class="progress"><div class="progress-bar" style="width:'+pct+'%"></div></div>'
                 + '<div class="progress-text">'+progText+'</div></div>';
    }}

    const execClass = d.executable ? ' executable' : '';
    const date = d.completed_at || d.created_at || '';
    let loc = '';
    try {{ loc = String(d.save_path).replace(/\\\\/g,'/').split('/').slice(0,-1).join('/'); }} catch (e) {{}}
    const errHtml = d.error_message ? ' <span class="err">— ' + esc(d.error_message) + '</span>' : '';

    return '<div class="item'+execClass+'" data-id="'+d.id+'">'
        + '<div class="icon">'+iconFor(d.filename)+'</div>'
        + '<div class="meta"><div class="name" title="'+esc(d.filename)+'">'+esc(d.filename)+'</div>'
        + '<div class="status">'+fmtStatus(d)+errHtml+'</div>'
        + '<div class="details">'+esc(date)+(loc ? ' · '+esc(loc) : '')+'</div>'
        + progress + '</div>'
        + '<div class="actions">'+actions+'</div></div>';
}}

function render() {{
    const q = document.getElementById('search').value.trim().toLowerCase();
    let items = ALL_DOWNLOADS;
    if (q) {{
        items = items.filter(d =>
            (d.filename||'').toLowerCase().includes(q) ||
            (d.url||'').toLowerCase().includes(q) ||
            (d.status||'').toLowerCase().includes(q) ||
            (d.mime_type||'').toLowerCase().includes(q));
    }}

    const active = items.filter(d => ['QUEUED','DOWNLOADING','PAUSED'].includes((d.status||'').toUpperCase()));
    const failed = items.filter(d => ['FAILED','CANCELLED','INTERRUPTED'].includes((d.status||'').toUpperCase()));
    const completed = items.filter(d => (d.status||'').toUpperCase() === 'COMPLETED');

    const sections = document.getElementById('sections');
    sections.innerHTML = '';

    function addSection(title, list, idPrefix) {{
        if (!list.length) return;
        const sec = document.createElement('div');
        sec.className = 'section';
        sec.innerHTML = '<div class="section-title">'+esc(title)+' <span class="count">('+list.length+')</span></div>'
            + '<div class="list">'+list.map(renderItem).join('')+'</div>';
        sections.appendChild(sec);
    }}

    addSection('Active', active, 'active');
    addSection('Failed', failed, 'failed');
    addSection('Completed', completed, 'completed');

    document.getElementById('empty-msg').style.display = items.length ? 'none' : 'block';

    sections.querySelectorAll('[data-href]').forEach(el => {{
        el.addEventListener('click', e => {{
            e.preventDefault();
            e.stopPropagation();
            window.location.href = el.dataset.href;
        }});
    }});

    sections.querySelectorAll('.item').forEach(el => {{
        el.addEventListener('click', e => {{
            if (e.target.closest('.actions')) return;
            const id = el.dataset.id;
            const d = items.find(x => String(x.id) === String(id));
            if (!d) return;
            if ((d.status||'').toUpperCase() === 'COMPLETED') window.location.href = actionUrl(id, 'open');
        }});
    }});
}}

document.getElementById('search').addEventListener('input', render);
document.getElementById('clear-btn').addEventListener('click', () => {{
    window.location.href = 'rhodium://downloads-clear';
}});

render();
</script>
</body>
</html>"""
