import base64
import html as html_module
import urllib.parse
import os
from urllib.parse import urlparse

from rhodium.theme import qss, css_vars, token

def get_stylesheet() -> str:
    return qss()

def _shortcut_icon_html(shortcut: dict, fallback_icon: str) -> str:
    """Build a shortcut icon img tag. Uses base64 for local files because QWebEngine blocks file:// in setHtml()."""
    fav_path = shortcut.get("favicon", "")
    if fav_path and os.path.exists(fav_path):
        try:
            with open(fav_path, "rb") as handle:
                data = handle.read()
            ext = os.path.splitext(fav_path)[1].lower()
            mime = {
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".gif": "image/gif",
                ".webp": "image/webp",
                ".ico": "image/x-icon",
            }.get(ext, "image/png")
            encoded = base64.b64encode(data).decode("ascii")
            return f'<img src="data:{mime};base64,{encoded}" alt="" class="shortcut-favicon" />'
        except OSError:
            pass

    url = shortcut.get("url", "")
    domain = urlparse(url).netloc
    if domain:
        remote = html_module.escape(
            f"https://www.google.com/s2/favicons?sz=64&domain={domain}",
            quote=True,
        )
        return f'<img src="{remote}" alt="" class="shortcut-favicon" />'

    return fallback_icon


def get_home_page_html(shortcuts=None) -> str:
    if shortcuts is None:
        shortcuts = []

    fallback_icon = """
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"
             stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <circle cx="12" cy="12" r="9"/>
            <path d="M3 12h18"/>
            <path d="M12 3c2.8 2.6 4.2 5.7 4.2 9s-1.4 6.4-4.2 9"/>
            <path d="M12 3C9.2 5.6 7.8 8.7 7.8 12s1.4 6.4 4.2 9"/>
        </svg>
    """

    shortcuts_html = ""
    for i, s in enumerate(shortcuts):
        name = html_module.escape(s.get("name", "Shortcut"))
        url = s.get("url", "#")
        url_attr = html_module.escape(url, quote=True)
        edit_href = html_module.escape(
            f"rhodium://edit-shortcut?url={urllib.parse.quote(url, safe='')}",
            quote=True,
        )
        delete_href = html_module.escape(
            f"rhodium://delete-shortcut?url={urllib.parse.quote(url, safe='')}",
            quote=True,
        )
        icon_element = _shortcut_icon_html(s, fallback_icon)

        shortcuts_html += f"""
            <article class="shortcut-card" data-url="{url_attr}" style="animation-delay:{i * 40}ms">
                <div class="shortcut-actions">
                    <button type="button" class="shortcut-action edit" data-href="{edit_href}" title="Edit" aria-label="Edit {name}">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"
                             stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.8 2.8 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/></svg>
                    </button>
                    <button type="button" class="shortcut-action delete" data-href="{delete_href}" title="Remove" aria-label="Remove {name}">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"
                             stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18M8 6V4h8v2M6 6l1 14h10l1-14"/></svg>
                    </button>
                </div>
                <button type="button" class="shortcut-main" aria-label="Open {name}">
                    <span class="shortcut-icon">{icon_element}</span>
                    <span class="shortcut-label">{name}</span>
                </button>
            </article>
        """

    shortcuts_html += """
        <button type="button" class="shortcut-card add" id="add-shortcut" style="animation-delay:400ms">
            <span class="shortcut-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"
                     stroke-linecap="round" aria-hidden="true">
                    <path d="M12 5v14"/>
                    <path d="M5 12h14"/>
                </svg>
            </span>
            <span class="shortcut-label">Add shortcut</span>
        </button>
    """    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Rhodium</title>
<style>
* {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}}

{css_vars()}

html, body {{
    width: 100%;
    height: 100%;
    background: var(--bg_app);
}}

body {{
    color: var(--text_primary);
    font-family: "Segoe UI", "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
    user-select: none;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    position: relative;
}}

/* Immersive animated gradient backdrop */
.backdrop {{
    position: fixed;
    inset: 0;
    z-index: 0;
    background:
        radial-gradient(60% 55% at 18% 18%, #EDE8FD 0%, transparent 60%),
        radial-gradient(55% 50% at 82% 12%, #E3E9FA 0%, transparent 55%),
        radial-gradient(60% 60% at 78% 82%, #EFE7FB 0%, transparent 60%),
        radial-gradient(50% 55% at 15% 80%, #E8F2FA 0%, transparent 55%),
        linear-gradient(160deg, #F7F6FB 0%, #F3F5FA 100%);
}}

.backdrop .orb {{
    position: absolute;
    border-radius: 50%;
    filter: blur(60px);
    opacity: .55;
    will-change: transform;
    animation: drift 22s ease-in-out infinite alternate;
}}

.backdrop .orb.o1 {{
    width: 440px; height: 440px;
    left: -120px; top: -120px;
    background: #CDBDF5;
    animation-duration: 26s;
}}

.backdrop .orb.o2 {{
    width: 380px; height: 380px;
    right: -100px; top: -60px;
    background: #B9CBF2;
    animation-duration: 30s;
    animation-delay: -8s;
}}

.backdrop .orb.o3 {{
    width: 460px; height: 460px;
    left: 30%; bottom: -200px;
    background: #D8C6F2;
    animation-duration: 34s;
    animation-delay: -16s;
}}

@keyframes drift {{
    from {{ transform: translate3d(0, 0, 0) scale(1); }}
    to   {{ transform: translate3d(30px, -24px, 0) scale(1.08); }}
}}

.page {{
    position: relative;
    z-index: 1;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 32px 24px;
}}

.shell {{
    width: min(720px, 100%);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 30px;
    animation: rise .55s cubic-bezier(.22, 1, .36, 1) both;
}}

@keyframes rise {{
    from {{ opacity: 0; transform: translateY(16px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}

.hero {{
    text-align: center;
}}

.eyebrow {{
    font-size: 11px;
    font-weight: 600;
    letter-spacing: .22em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 12px;
}}

.brand {{
    display: inline-flex;
    align-items: center;
    gap: 12px;
    padding: 8px 16px 8px 8px;
    border-radius: 999px;
    background: rgba(255, 255, 255, .65);
    border: 1px solid rgba(255, 255, 255, .9);
    box-shadow: var(--shadow_sm);
    backdrop-filter: blur(8px);
}}

.brand-mark {{
    width: 34px;
    height: 34px;
    display: grid;
    place-items: center;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--accent) 0%, #8B6FE0 100%);
    box-shadow: 0 4px 12px rgba(109, 79, 216, .35);
}}

.brand-mark svg {{
    width: 18px;
    height: 18px;
    stroke: #FFFFFF;
}}

.brand-name {{
    font-size: 19px;
    font-weight: 700;
    letter-spacing: -.02em;
    color: var(--text_primary);
}}

.search-panel {{
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 10px;
}}

.search {{
    display: flex;
    align-items: center;
    height: 58px;
    padding: 0 18px;
    border-radius: 16px;
    background: rgba(255, 255, 255, .86);
    border: 1px solid rgba(216, 219, 228, .9);
    box-shadow: var(--shadow_md);
    transition: border-color .18s ease, box-shadow .18s ease, background .18s ease;
    backdrop-filter: blur(10px);
}}

.search:hover {{
    border-color: var(--border_strong);
}}

.search:focus-within {{
    border-color: var(--accent);
    box-shadow: 0 0 0 4px var(--accent_soft), var(--shadow_md);
    background: #FFFFFF;
}}

.search-icon {{
    width: 20px;
    height: 20px;
    margin-right: 14px;
    color: var(--text_secondary);
    flex-shrink: 0;
}}

.search input {{
    width: 100%;
    border: none;
    outline: none;
    background: transparent;
    color: var(--text_primary);
    font-size: 15px;
}}

.search input::placeholder {{
    color: var(--text_muted);
}}

.search-hint {{
    text-align: center;
    color: var(--text_muted);
    font-size: 11px;
}}

.shortcuts-section {{
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 14px;
}}

.section-head {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 4px;
}}

.section-title {{
    color: var(--text_secondary);
    font-size: 11px;
    font-weight: 600;
    letter-spacing: .08em;
    text-transform: uppercase;
}}

.section-count {{
    color: var(--text_muted);
    font-size: 11px;
}}

.shortcuts {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(108px, 1fr));
    gap: 12px;
    width: 100%;
}}

.shortcut-card {{
    position: relative;
    border: none;
    background: transparent;
    padding: 0;
    text-align: center;
    animation: rise .45s cubic-bezier(.22, 1, .36, 1) both;
}}

.shortcut-main,
.shortcut-card.add {{
    width: 100%;
    padding: 12px 8px 10px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
    border-radius: 16px;
    border: 1px solid transparent;
    background: transparent;
    color: var(--text_secondary);
    cursor: pointer;
    transition: background .18s, border-color .18s, transform .18s, box-shadow .18s;
}}

.shortcut-main:hover,
.shortcut-card.add:hover {{
    background: rgba(255, 255, 255, .7);
    border-color: var(--border);
    box-shadow: var(--shadow_md);
    transform: translateY(-2px);
    color: var(--text_primary);
}}

.shortcut-icon {{
    width: 52px;
    height: 52px;
    display: grid;
    place-items: center;
    border-radius: 16px;
    background: rgba(255, 255, 255, .9);
    border: 1px solid var(--border);
    box-shadow: var(--shadow_sm);
    transition: transform .18s;
}}

.shortcut-main:hover .shortcut-icon,
.shortcut-card.add:hover .shortcut-icon {{
    transform: scale(1.06);
}}

.shortcut-icon svg {{
    width: 22px;
    height: 22px;
    stroke: var(--accent);
}}

.shortcut-favicon {{
    width: 26px;
    height: 26px;
    border-radius: 6px;
    object-fit: contain;
}}

.shortcut-label {{
    max-width: 100%;
    font-size: 12px;
    font-weight: 500;
    line-height: 1.2;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}

.shortcut-actions {{
    position: absolute;
    top: 6px;
    right: 6px;
    display: flex;
    gap: 4px;
    opacity: 0;
    transform: translateY(-2px);
    transition: opacity .15s, transform .15s;
    z-index: 2;
}}

.shortcut-card:hover .shortcut-actions {{
    opacity: 1;
    transform: translateY(0);
}}

.shortcut-action {{
    width: 26px;
    height: 26px;
    display: grid;
    place-items: center;
    border: 1px solid var(--border);
    background: rgba(255, 255, 255, .92);
    color: var(--text_secondary);
    border-radius: 8px;
    font-size: 10px;
    cursor: pointer;
    box-shadow: var(--shadow_sm);
    transition: background .15s, color .15s;
}}

.shortcut-action svg {{
    width: 14px;
    height: 14px;
}}

.shortcut-action:hover {{
    background: var(--bg_hover);
    color: var(--text_primary);
}}

.shortcut-action.delete {{
    color: var(--danger);
}}

.shortcut-action.delete:hover {{
    background: var(--danger_soft);
    color: var(--danger);
}}

.footer {{
    text-align: center;
    color: var(--text_muted);
    font-size: 11px;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding-top: 4px;
}}
</style>
</head>
<body>

<div class="backdrop" aria-hidden="true">
    <div class="orb o1"></div>
    <div class="orb o2"></div>
    <div class="orb o3"></div>
</div>

<main class="page">
    <div class="shell">

        <header class="hero">
            <div class="eyebrow">Welcome back</div>
            <div class="brand">
                <div class="brand-mark">
                    <svg viewBox="0 0 24 24" fill="none" stroke-width="1.8"
                         stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                        <circle cx="12" cy="12" r="8.5"/>
                        <path d="M3.8 12h16.4"/>
                        <path d="M12 3.5c2.4 2.3 3.6 5.1 3.6 8.5S14.4 18.2 12 20.5"/>
                        <path d="M12 3.5C9.6 5.8 8.4 8.6 8.4 12s1.2 6.2 3.6 8.5"/>
                    </svg>
                </div>
                <span class="brand-name">Rhodium</span>
            </div>
        </header>

        <section class="search-panel">
            <div class="search">
                <svg class="search-icon" viewBox="0 0 24 24" fill="none"
                     stroke="currentColor" stroke-width="1.8" stroke-linecap="round" aria-hidden="true">
                    <circle cx="11" cy="11" r="6.5"/>
                    <path d="m16 16 4 4"/>
                </svg>
                <input id="q" type="text" placeholder="Search the web or enter an address"
                       autocomplete="off" spellcheck="false" autofocus>
            </div>
            <p class="search-hint">Press Enter to search or navigate</p>
        </section>

        <section class="shortcuts-section">
            <div class="section-head">
                <span class="section-title">Quick access</span>
                <span class="section-count" id="shortcut-count"></span>
            </div>
            <div class="shortcuts" id="shortcuts">
                {shortcuts_html}
            </div>
        </section>

        <footer class="footer">Fast · Private · Yours</footer>
    </div>
</main>

<script>
(function () {{
    const searchInput = document.getElementById('q');
    const countEl = document.getElementById('shortcut-count');

    function nav(query) {{
        window.location.href = 'rhodium://navigate?q=' + encodeURIComponent(query);
    }}

    const cards = document.querySelectorAll('.shortcut-card[data-url]');
    countEl.textContent = cards.length + ' saved';

    cards.forEach(card => {{
        const main = card.querySelector('.shortcut-main');
        main.addEventListener('click', () => {{
            const url = card.dataset.url;
            if (url) nav(url);
        }});
    }});

    document.querySelectorAll('.shortcut-action').forEach(btn => {{
        btn.addEventListener('click', event => {{
            event.stopPropagation();
            const href = btn.dataset.href;
            if (href) window.location.href = href;
        }});
    }});

    document.getElementById('add-shortcut').addEventListener('click', () => {{
        window.location.href = 'rhodium://add-shortcut';
    }});

    searchInput.addEventListener('keydown', event => {{
        if (event.key === 'Enter') {{
            const value = searchInput.value.trim();
            if (value) nav(value);
        }} else if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {{
            event.preventDefault();
            window.location.href = 'rhodium://suggest-key?key=' + event.key;
        }} else if (event.key === 'Escape') {{
            window.location.href = 'rhodium://suggest-key?key=Escape';
        }}
    }});

    // Local previous-search suggestions (Phase 1, offline)
    let suggestTimer = null;

    searchInput.addEventListener('input', () => {{
        clearTimeout(suggestTimer);
        const value = searchInput.value.trim();
        if (value.length < 2) {{
            window.location.href = 'rhodium://suggest-hide';
            return;
        }}
        suggestTimer = setTimeout(() => {{
            window.location.href =
                'rhodium://suggest?query=' + encodeURIComponent(value);
        }}, 180);
    }});

    searchInput.addEventListener('blur', () => {{
        setTimeout(() => {{
            if (document.activeElement !== searchInput) {{
                window.location.href = 'rhodium://suggest-hide';
            }}
        }}, 200);
    }});
}})();
</script>
</body>
</html>"""


def get_offline_page_html(failed_url="") -> str:
    """
    Generate the Rhodium offline/error page.

    Args:
        failed_url: The URL that failed to load.

    Returns:
        Complete HTML document for the offline page.
    """

    # Safely display the failed URL inside HTML.
    failed_url_display = failed_url or "The requested page"

    # Prevent HTML injection / broken markup.
    failed_url_display = (
        failed_url_display
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>Rhodium — Offline</title>

    <style>
        {css_vars()}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        html,
        body {{
            width: 100%;
            height: 100%;
            background: var(--bg_app);
        }}

        body {{
            color: var(--text_primary);
            font-family: "Segoe UI", "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            overflow: hidden;
            user-select: none;
            position: relative;
            background:
                radial-gradient(55% 50% at 20% 20%, #EDE8FD 0%, transparent 60%),
                radial-gradient(55% 50% at 82% 18%, #E3E9FA 0%, transparent 55%),
                radial-gradient(60% 60% at 78% 82%, #EFE7FB 0%, transparent 60%),
                linear-gradient(160deg, #F7F6FB 0%, #F3F5FA 100%);
        }}

        .container {{
            position: relative;
            z-index: 1;
            width: 480px;
            max-width: calc(100vw - 40px);
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            background: rgba(255, 255, 255, .78);
            border: 1px solid rgba(255, 255, 255, .9);
            border-radius: 24px;
            padding: 40px 36px;
            box-shadow: var(--shadow_lg);
            backdrop-filter: blur(12px);
        }}

        .icon-container {{
            width: 64px;
            height: 64px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 18px;
            background: var(--accent_soft);
            border: 1px solid var(--accent_soft_hover);
            margin-bottom: 22px;
        }}

        .icon-container svg {{
            width: 30px;
            height: 30px;
            stroke: var(--accent);
        }}

        h1 {{
            color: var(--text_primary);
            font-size: 21px;
            font-weight: 700;
            letter-spacing: -0.3px;
            margin-bottom: 8px;
        }}

        .description {{
            color: var(--text_secondary);
            font-size: 12px;
            line-height: 1.5;
            max-width: 360px;
            margin-bottom: 18px;
        }}

        .url {{
            width: 100%;
            max-width: 380px;
            background: var(--bg_sunken);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 9px 14px;
            color: var(--text_muted);
            font-size: 11px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            margin-bottom: 22px;
        }}

        .buttons {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }}

        button {{
            height: 38px;
            padding: 0 18px;
            border-radius: 10px;
            border: 1px solid var(--border_strong);
            background: var(--bg_surface);
            color: var(--text_secondary);
            font-family: inherit;
            font-size: 12px;
            cursor: pointer;
            transition: background .15s, border-color .15s, color .15s;
        }}

        button:hover {{
            background: var(--bg_hover);
            border-color: var(--border_strong);
            color: var(--text_primary);
        }}

        .primary {{
            background: var(--accent);
            border-color: var(--accent);
            color: var(--on_accent);
            font-weight: 600;
        }}

        .primary:hover {{
            background: var(--accent_hover);
            border-color: var(--accent_hover);
            color: var(--on_accent);
        }}

        .footer {{
            margin-top: 30px;
            color: var(--text_muted);
            font-size: 10px;
            letter-spacing: 2px;
        }}

    </style>
</head>

<body>

    <div class="container">

        <div class="icon-container">
            <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1.7"
                stroke-linecap="round"
                stroke-linejoin="round"
            >
                <path d="M1 1l22 22"/>
                <path d="M9.9 4.2a10.8 10.8 0 0 1 8.9 3.4"/>
                <path d="M5.3 8.8a7.5 7.5 0 0 1 5.8-1.7"/>
                <path d="M2.7 12.9a4.5 4.5 0 0 1 3.4-1.2"/>
                <path d="M12 19h.01"/>
                <path d="M16.7 13.3a3.8 3.8 0 0 0-2.8-1.1"/>
            </svg>
        </div>

        <h1>No Internet Connection</h1>

        <div class="description">
            Rhodium couldn't load this page.
            Check your internet connection and try again.
        </div>

        <div class="url" title="{failed_url_display}">
            {failed_url_display}
        </div>

        <div class="buttons">
            <button onclick="goHome()">Go Home</button>
            <button class="primary" onclick="retry()">Try Again</button>
        </div>

        <div class="footer">RHODIUM</div>

    </div>

    <script>
        function retry() {{
            window.location.href = 'rhodium://retry';
        }}

        function goHome() {{
            window.location.href = 'rhodium://home';
        }}
    </script>

</body>
</html>"""


def get_downloads_page_html(downloads_json: str = "[]") -> str:
    """Generate the rhodium://downloads internal page."""
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
    background: var(--bg_app);
    color: var(--text_primary);
    font-family: "Segoe UI", Inter, -apple-system, BlinkMacSystemFont, sans-serif;
    min-height: 100vh;
}}
.page {{ max-width: 920px; margin: 0 auto; padding: 36px 24px 56px; }}
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
    font-size: 11px; font-weight: 700; letter-spacing: .1em;
    text-transform: uppercase; color: var(--text_muted); margin-bottom: 12px;
}}
.list {{ display: flex; flex-direction: column; gap: 8px; }}
.item {{
    background: var(--bg_surface); border: 1px solid var(--border); border-radius: 14px;
    padding: 14px 16px; display: grid; grid-template-columns: 40px 1fr auto;
    gap: 14px; align-items: start; transition: border-color .15s, box-shadow .15s;
}}
.item:hover {{ border-color: var(--border_strong); box-shadow: var(--shadow_sm); }}
.item.executable {{ border-left: 3px solid var(--warning); }}
.icon {{
    width: 38px; height: 38px; border-radius: 11px;
    background: var(--bg_sunken); display: grid; place-items: center; font-size: 18px;
}}
.meta {{ min-width: 0; }}
.name {{
    font-size: 13px; font-weight: 600; color: var(--text_primary);
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}}
.status {{ font-size: 11px; color: var(--text_secondary); margin-top: 3px; }}
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
    <div class="section" id="active-section" style="display:none">
        <div class="section-title">Active downloads</div>
        <div class="list" id="active-list"></div>
    </div>
    <div class="section">
        <div class="section-title" id="recent-title">Recent downloads</div>
        <div class="list" id="recent-list"></div>
        <div class="empty" id="empty-msg" style="display:none">
            <div class="big">⬇️</div>
            <div>No downloads yet</div>
        </div>
    </div>
</div>
<script>
const ALL_DOWNLOADS = {downloads_json};

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
    return 'rhodium://download-action?id='+id+'&action='+action;
}}

function renderItem(d) {{
    const active = ['QUEUED','DOWNLOADING','PAUSED'].includes((d.status||'').toUpperCase());
    const pct = d.total_size > 0 ? Math.min(100, Math.round(d.downloaded_size*100/d.total_size)) : 0;
    let actions = '';
    const s = (d.status||'').toUpperCase();
    if (s === 'COMPLETED') {{
        actions += '<button class="action primary" data-href="'+actionUrl(d.id,'open')+'">Open</button>';
        actions += '<button class="action" data-href="'+actionUrl(d.id,'folder')+'">Show in folder</button>';
    }}
    if (['FAILED','CANCELLED','INTERRUPTED'].includes(s))
        actions += '<button class="action primary" data-href="'+actionUrl(d.id,'retry')+'">Retry</button>';
    if (active) {{
        if (s === 'PAUSED')
            actions += '<button class="action" data-href="'+actionUrl(d.id,'resume')+'">Resume</button>';
        else
            actions += '<button class="action" data-href="'+actionUrl(d.id,'pause')+'">Pause</button>';
        actions += '<button class="action" data-href="'+actionUrl(d.id,'cancel')+'">Cancel</button>';
    }}
    actions += '<button class="action" data-href="'+actionUrl(d.id,'remove')+'">Remove</button>';
    if (s === 'COMPLETED')
        actions += '<button class="action" data-href="'+actionUrl(d.id,'delete')+'">Delete file</button>';

    let progress = '';
    if (active) {{
        const progText = d.total_size > 0
            ? fmtBytes(d.downloaded_size)+' / '+fmtBytes(d.total_size)+' · '+pct+'%'
            : fmtBytes(d.downloaded_size)+' · Downloading…';
        progress = '<div class="progress-wrap"><div class="progress"><div class="progress-bar" style="width:'+pct+'%"></div></div>'
                 + '<div class="progress-text">'+progText+'</div></div>';
    }}

    const execClass = d.executable ? ' executable' : '';
    const date = d.completed_at || d.created_at || '';
    const loc = d.path ? String(d.path).replace(/\\/g,'/').split('/').slice(0,-1).join('/') : '';

    return '<div class="item'+execClass+'" data-id="'+d.id+'">'
        + '<div class="icon">'+iconFor(d.filename)+'</div>'
        + '<div class="meta"><div class="name" title="'+d.filename+'">'+d.filename+'</div>'
        + '<div class="status">'+fmtStatus(d)+(d.error_message ? ' — '+d.error_message : '')+'</div>'
        + '<div class="details">'+date+(loc ? ' · '+loc : '')+'</div>'
        + progress + '</div>'
        + '<div class="actions">'+actions+'</div></div>';
}}

function render(list) {{
    const q = document.getElementById('search').value.trim().toLowerCase();
    let items = list;
    if (q) {{
        items = list.filter(d =>
            (d.filename||'').toLowerCase().includes(q) ||
            (d.url||'').toLowerCase().includes(q) ||
            (d.status||'').toLowerCase().includes(q) ||
            (d.mime_type||'').toLowerCase().includes(q)
        );
    }}
    const active = items.filter(d => ['QUEUED','DOWNLOADING','PAUSED'].includes((d.status||'').toUpperCase()));
    const recent = items.filter(d => !['QUEUED','DOWNLOADING','PAUSED'].includes((d.status||'').toUpperCase()));

    const activeSec = document.getElementById('active-section');
    const activeList = document.getElementById('active-list');
    activeList.innerHTML = active.map(renderItem).join('');
    activeSec.style.display = active.length ? 'block' : 'none';

    const recentList = document.getElementById('recent-list');
    recentList.innerHTML = recent.map(renderItem).join('');
    document.getElementById('empty-msg').style.display = items.length ? 'none' : 'block';
    document.getElementById('recent-title').textContent =
        active.length ? 'Recent downloads' : 'Downloads';

    document.querySelectorAll('[data-href]').forEach(el => {{
        el.addEventListener('click', e => {{
            e.preventDefault();
            window.location.href = el.dataset.href;
        }});
    }});

    document.querySelectorAll('.item').forEach(el => {{
        el.addEventListener('click', e => {{
            if (e.target.closest('.actions')) return;
            const id = el.dataset.id;
            const d = list.find(x => String(x.id) === String(id));
            if (!d) return;
            const s = (d.status||'').toUpperCase();
            if (s === 'COMPLETED') window.location.href = actionUrl(id, 'open');
        }});
    }});
}}

document.getElementById('search').addEventListener('input', () => render(ALL_DOWNLOADS));
document.getElementById('clear-btn').addEventListener('click', () => {{
    window.location.href = 'rhodium://downloads-clear';
}});

render(ALL_DOWNLOADS);
</script>
</body>
</html>"""


def get_history_page_html(history_json: str = "[]") -> str:
    """Generate the rhodium://history internal page.

    `history_json` is a JSON array of rows produced by RhodiumDatabase.get_history.
    Each row: {"url", "title", "visit_count", "last_visited"} where last_visited
    is an ISO timestamp in local time.
    """
    safe_json = history_json.replace("</", "<\\/")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>History — Rhodium</title>
<style>
{css_vars()}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
    background: var(--bg_app); color: var(--text_primary);
    font-family: "Segoe UI", Inter, -apple-system, BlinkMacSystemFont, sans-serif;
    min-height: 100vh;
}}
.page {{ max-width: 920px; margin: 0 auto; padding: 36px 24px 56px; }}
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
.header-actions {{ display: flex; gap: 10px; align-items: center; flex: 1; justify-content: flex-end; position: relative; }}
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
.clear-menu {{
    position: absolute; top: 46px; right: 0; z-index: 20;
    background: var(--bg_surface); border: 1px solid var(--border_strong); border-radius: 12px;
    padding: 6px; min-width: 210px; box-shadow: var(--shadow_lg);
    display: none;
}}
.clear-menu.open {{ display: block; }}
.clear-menu button {{
    display: block; width: 100%; text-align: left; background: none; border: none;
    color: var(--text_secondary); padding: 10px 12px; font-size: 12.5px; border-radius: 8px; cursor: pointer;
}}
.clear-menu button:hover {{ background: var(--bg_hover); color: var(--text_primary); }}
.clear-menu button.danger {{ color: var(--danger); }}
.clear-menu button.danger:hover {{ background: var(--danger_soft); color: var(--danger); }}
.section {{ margin-bottom: 26px; }}
.section-title {{
    font-size: 11px; font-weight: 700; letter-spacing: .1em;
    text-transform: uppercase; color: var(--text_muted); margin: 18px 4px 10px;
}}
.list {{ display: flex; flex-direction: column; gap: 6px; }}
.item {{
    background: var(--bg_surface); border: 1px solid var(--border); border-radius: 12px;
    padding: 10px 14px; display: grid; grid-template-columns: 34px 1fr auto;
    gap: 12px; align-items: center; transition: border-color .15s, box-shadow .15s;
    cursor: pointer;
}}
.item:hover {{ border-color: var(--border_strong); box-shadow: var(--shadow_sm); }}
.fav-wrap {{
    width: 32px; height: 32px; border-radius: 9px; background: var(--bg_sunken);
    display: grid; place-items: center; overflow: hidden; font-size: 15px;
}}
.fav-wrap img {{ width: 22px; height: 22px; }}
.meta {{ min-width: 0; }}
.title {{
    font-size: 13px; font-weight: 600; color: var(--text_primary);
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}}
.sub {{ font-size: 11px; color: var(--text_secondary); margin-top: 2px;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.time {{ font-size: 11px; color: var(--text_muted); white-space: nowrap; padding-right: 4px; }}
.del {{
    background: var(--bg_sunken); color: var(--text_secondary); border: none; border-radius: 8px;
    padding: 6px 11px; font-size: 11px; cursor: pointer; opacity: 0; transition: opacity .15s, background .15s, color .15s;
}}
.item:hover .del {{ opacity: 1; }}
.del:hover {{ background: var(--danger_soft); color: var(--danger); }}
.empty {{ text-align: center; color: var(--text_muted); padding: 48px 20px; font-size: 13px; }}
.empty .big {{ font-size: 42px; opacity: .5; margin-bottom: 12px; }}
</style>
</head>
<body>
<div class="page">
    <div class="header">
        <div class="heading">
            <div class="heading-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"
                     stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>
            </div>
            <div>
                <h1>History</h1>
                <div class="sub">Your browsing timeline</div>
            </div>
        </div>
        <div class="header-actions">
            <input type="search" class="search" id="search" placeholder="Search history…">
            <button class="btn btn-danger" id="clear-btn">Clear</button>
            <div class="clear-menu" id="clear-menu">
                <button data-range="hour">Last hour</button>
                <button data-range="today">Today</button>
                <button data-range="yesterday">Today &amp; yesterday</button>
                <button class="danger" data-range="all">All history</button>
            </div>
        </div>
    </div>
    <div id="content"></div>
    <div class="empty" id="empty-msg" style="display:none">
        <div class="big">🕘</div>
        <div>No history found</div>
    </div>
</div>
<script>
const ALL_HISTORY = {safe_json};

function domainOf(url) {{
    try {{ return new URL(url).hostname; }} catch (e) {{ return ''; }}
}}
function pad(n) {{ return n < 10 ? '0' + n : '' + n; }}
function fmtTime(d) {{
    return pad(d.getHours()) + ':' + pad(d.getMinutes());
}}
function fmtDay(d) {{
    const days = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
    return days[d.getDay()] + ' ' + fmtTime(d);
}}
function fmtOld(d) {{
    const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    return pad(d.getDate()) + ' ' + months[d.getMonth()] + ' ' + d.getFullYear() + ' ' + fmtTime(d);
}}
function bucketOf(iso) {{
    const d = new Date(iso.replace(' ', 'T'));
    if (isNaN(d)) return 'older';
    const now = new Date();
    const dayMs = 86400000;
    const todayMid = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime();
    const itemMid = new Date(d.getFullYear(), d.getMonth(), d.getDate()).getTime();
    const diff = Math.round((todayMid - itemMid) / dayMs);
    if (diff <= 0) return 'today';
    if (diff === 1) return 'yesterday';
    if (diff <= 7) return 'week';
    return 'older';
}}
function renderTime(iso, bucket) {{
    const d = new Date(iso.replace(' ', 'T'));
    if (isNaN(d)) return '';
    if (bucket === 'today') return fmtTime(d);
    if (bucket === 'yesterday') return 'Yesterday ' + fmtTime(d);
    if (bucket === 'week') return fmtDay(d);
    return fmtOld(d);
}}
function escapeHtml(s) {{
    return String(s == null ? '' : s)
        .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
        .replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}}

function renderItem(it) {{
    const bucket = bucketOf(it.last_visited);
    const dom = domainOf(it.url);
    const title = it.title && it.title.trim() ? it.title : it.url;
    const visits = (it.visit_count > 1) ? ' · ' + it.visit_count + ' visits' : '';
    const fav = dom
        ? '<img src="https://www.google.com/s2/favicons?sz=32&domain=' + encodeURIComponent(dom)
          + '" onerror="this.style.display=&quot;none&quot;;this.parentNode.textContent=&quot;🌐&quot;">'
        : '🌐';
    const href = 'rhodium://navigate?q=' + encodeURIComponent(it.url);
    const delHref = 'rhodium://history-action?action=delete&url=' + encodeURIComponent(it.url);
    return '<div class="item" data-href="' + href + '">'
        + '<div class="fav-wrap">' + fav + '</div>'
        + '<div class="meta"><div class="title">' + escapeHtml(title) + '</div>'
        + '<div class="sub">' + escapeHtml(it.url) + visits + '</div></div>'
        + '<div style="display:flex;align-items:center;gap:10px">'
        + '<span class="time">' + renderTime(it.last_visited, bucket) + '</span>'
        + '<button class="del" data-del="' + delHref + '">Delete</button>'
        + '</div></div>';
}}

function render() {{
    const q = document.getElementById('search').value.trim().toLowerCase();
    let items = ALL_HISTORY.filter(it => {{
        if (!q) return true;
        const t = (it.title || '').toLowerCase();
        const u = (it.url || '').toLowerCase();
        return t.includes(q) || u.includes(q);
    }});

    const buckets = [
        ['today', 'Today'],
        ['yesterday', 'Yesterday'],
        ['week', 'Previous 7 Days'],
        ['older', 'Older']
    ];
    const content = document.getElementById('content');
    content.innerHTML = '';
    let total = 0;
    for (const [key, label] of buckets) {{
        const group = items.filter(it => bucketOf(it.last_visited) === key);
        if (!group.length) continue;
        total += group.length;
        const sec = document.createElement('div');
        sec.className = 'section';
        sec.innerHTML = '<div class="section-title">' + label + '</div>'
            + '<div class="list">' + group.map(renderItem).join('') + '</div>';
        content.appendChild(sec);
    }}
    document.getElementById('empty-msg').style.display = total ? 'none' : 'block';

    content.querySelectorAll('.item').forEach(el => {{
        el.addEventListener('click', e => {{
            if (e.target.closest('.del')) return;
            window.location.href = el.dataset.href;
        }});
    }});
    content.querySelectorAll('.del').forEach(el => {{
        el.addEventListener('click', e => {{
            e.stopPropagation();
            window.location.href = el.dataset.del;
        }});
    }});
}}

const clearBtn = document.getElementById('clear-btn');
const clearMenu = document.getElementById('clear-menu');
clearBtn.addEventListener('click', e => {{
    e.stopPropagation();
    clearMenu.classList.toggle('open');
}});
clearMenu.querySelectorAll('button').forEach(b => {{
    b.addEventListener('click', () => {{
        window.location.href = 'rhodium://history-clear?range=' + b.dataset.range;
    }});
}});
document.addEventListener('click', () => clearMenu.classList.remove('open'));

document.getElementById('search').addEventListener('input', render);
render();
</script>
</body>
</html>"""


def get_cookie_debugger_page_html(cookies_json: str = "[]", diagnostics_json: str = "{}") -> str:
    """Generate the rhodium://cookie-debugger internal page."""
    safe_cookies = (cookies_json or "[]").replace("</", "<\\/")
    safe_diag = (diagnostics_json or "{}").replace("</", "<\\/")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cookie Debugger — Rhodium</title>
<style>
{css_vars()}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg_app);color:var(--text_primary);font-family:"Segoe UI",Inter,-apple-system,BlinkMacSystemFont,sans-serif;min-height:100vh}}
.page{{max-width:1100px;margin:0 auto;padding:32px 24px 56px}}
.header{{display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;margin-bottom:22px}}
.header h1{{font-size:22px;font-weight:700;letter-spacing:-.02em;display:flex;align-items:center;gap:10px}}
.header h1 span.badge{{font-size:11px;font-weight:700;letter-spacing:.06em;padding:4px 9px;border-radius:999px;background:var(--accent_soft);border:1px solid var(--accent_soft_hover);color:var(--accent)}}
.sub{{color:var(--text_secondary);font-size:12px;margin-top:4px;max-width:720px;line-height:1.5}}
.status-row{{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-top:10px}}
.pill{{display:inline-flex;align-items:center;gap:6px;background:var(--bg_surface);border:1px solid var(--border_strong);border-radius:999px;padding:6px 11px;font-size:11px;color:var(--text_secondary)}}
.pill .dot{{width:8px;height:8px;border-radius:999px;background:var(--success);box-shadow:0 0 0 4px var(--success_soft)}}
.pill.off .dot{{background:var(--danger);box-shadow:0 0 0 4px var(--danger_soft)}}
.pill b{{color:var(--text_primary);font-weight:600}}
.card{{background:var(--bg_surface);border:1px solid var(--border);border-radius:16px;padding:16px 18px;margin-bottom:14px;box-shadow:var(--shadow_sm)}}
.card h2{{font-size:11px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--text_muted);margin-bottom:12px}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:10px}}
@media(max-width:760px){{.grid2{{grid-template-columns:1fr}}}}
.kv{{background:var(--bg_inset);border:1px solid var(--border);border-radius:10px;padding:11px 13px}}
.kv .k{{font-size:10px;letter-spacing:.07em;text-transform:uppercase;color:var(--text_muted);margin-bottom:4px}}
.kv .v{{font-size:12px;color:var(--text_primary);word-break:break-all}}
.kv .v.mono{{font-family:ui-monospace,Consolas,monospace;font-size:11px}}
.toolbar{{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-bottom:12px}}
.toolbar .left{{display:flex;gap:8px;align-items:center;flex-wrap:wrap;flex:1}}
.search{{background:var(--bg_sunken);border:1px solid transparent;border-radius:10px;color:var(--text_primary);padding:9px 13px;font-size:12.5px;width:min(360px,100%);outline:none;transition:border-color .15s,box-shadow .15s}}
.search:focus{{border-color:var(--accent);box-shadow:0 0 0 3px var(--accent_soft);background:var(--bg_surface)}}
.select, .input-sm{{background:var(--bg_sunken);border:1px solid transparent;border-radius:9px;color:var(--text_primary);padding:9px 11px;font-size:12px;outline:none;transition:border-color .15s}}
.select:focus,.input-sm:focus{{border-color:var(--accent);background:var(--bg_surface)}}
.btn{{background:var(--bg_sunken);color:var(--text_secondary);border:1px solid transparent;border-radius:9px;padding:9px 13px;font-size:12px;cursor:pointer;display:inline-flex;align-items:center;gap:6px;transition:background .15s,color .15s}}
.btn:hover{{background:var(--bg_hover);color:var(--text_primary)}}
.btn.primary{{background:var(--accent);color:var(--on_accent);font-weight:600}}
.btn.primary:hover{{background:var(--accent_hover);color:var(--on_accent)}}
.btn.danger{{background:var(--danger_soft);color:var(--danger)}}
.btn.danger:hover{{background:var(--danger);color:var(--on_accent)}}
.table-wrap{{overflow:auto;border:1px solid var(--border);border-radius:12px;background:var(--bg_surface)}}
table{{width:100%;border-collapse:collapse;min-width:860px}}
thead th{{text-align:left;font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:var(--text_muted);background:var(--bg_inset);padding:11px 12px;border-bottom:1px solid var(--border);position:sticky;top:0}}
tbody td{{padding:10px 12px;border-bottom:1px solid var(--border);font-size:12px;color:var(--text_primary);vertical-align:top;max-width:240px;word-break:break-all}}
tbody tr:last-child td{{border-bottom:none}}
tbody tr{{cursor:pointer}}
tbody tr:hover{{background:var(--bg_hover)}}
.badge-yes{{background:var(--success_soft);color:var(--success);border:1px solid var(--success_soft);padding:2px 7px;border-radius:999px;font-size:10px;font-weight:700}}
.badge-no{{background:var(--bg_sunken);color:var(--text_secondary);border:1px solid var(--border_strong);padding:2px 7px;border-radius:999px;font-size:10px;font-weight:700}}
.muted{{color:var(--text_muted)}}
.masked{{letter-spacing:2px}}
.empty{{text-align:center;color:var(--text_muted);padding:36px 16px;font-size:13px}}
.modal{{position:fixed;inset:0;background:rgba(24,26,34,.45);display:none;align-items:center;justify-content:center;padding:20px;z-index:50}}
.modal.open{{display:flex}}
.modal-card{{background:var(--bg_surface);border:1px solid var(--border_strong);border-radius:16px;max-width:620px;width:100%;padding:20px;max-height:85vh;overflow:auto;box-shadow:var(--shadow_lg)}}
.modal-card h3{{font-size:15px;margin-bottom:8px}}
.dl{{display:grid;grid-template-columns:140px 1fr;gap:8px;font-size:12px;margin-top:10px}}
.dl dt{{color:var(--text_muted)}}
.dl dd{{color:var(--text_primary);word-break:break-all;font-family:ui-monospace,Consolas,monospace;font-size:11px}}
.details-actions{{display:flex;gap:8px;margin-top:14px;flex-wrap:wrap}}
.chk{{display:inline-flex;align-items:center;gap:6px;font-size:11px;color:var(--text_secondary)}}
.raw{{background:var(--bg_inset);border:1px solid var(--border);border-radius:10px;padding:12px;font-family:ui-monospace,Consolas,monospace;font-size:11px;white-space:pre-wrap;word-break:break-all;color:var(--text_secondary);max-height:260px;overflow:auto}}
</style>
</head>
<body>
<div class="page">
  <div class="header">
    <div>
      <h1>Cookie Debugger <span class="badge">Developer</span></h1>
      <div class="sub">Inspect cookies stored by the current Rhodium profile. QtWebEngine's <b>QWebEngineCookieStore</b> remains the source of truth — nothing is deleted automatically.</div>
      <div class="status-row" id="statusRow"></div>
    </div>
    <div style="display:flex;gap:8px;align-items:center">
      <button class="btn primary" id="refreshBtn">↻ Refresh</button>
    </div>
  </div>

  <div class="card" id="statsCard"></div>

  <div class="card">
    <h2>Profile Diagnostics</h2>
    <div class="grid2" id="diagGrid"></div>
    <div style="margin-top:10px"><button class="btn" id="toggleRaw">Show Raw Debug Information</button></div>
    <div id="rawWrap" style="display:none;margin-top:10px"><div class="raw" id="rawBox"></div></div>
  </div>

  <div class="card">
    <h2>Cookies</h2>
    <div class="toolbar">
      <div class="left">
        <input class="search" id="search" placeholder="Search cookies... (name, domain, path)">
        <select class="select" id="typeFilter"><option value="all">All</option><option value="persistent">Persistent</option><option value="session">Session</option></select>
        <label class="chk"><input type="checkbox" id="secureOnly"> Secure only</label>
        <label class="chk"><input type="checkbox" id="httpOnlyOnly"> HttpOnly only</label>
      </div>
      <div style="display:flex;gap:8px">
        <button class="btn" id="clearFilter">Clear filters</button>
        <button class="btn danger" id="deleteAllBtn">Delete All Cookies</button>
      </div>
    </div>
    <div class="table-wrap">
      <table>
        <thead><tr><th>Name</th><th>Value</th><th>Domain</th><th>Path</th><th>Session</th><th>Secure</th><th>HttpOnly</th><th>SameSite</th><th>Expiration</th><th></th></tr></thead>
        <tbody id="tbody"></tbody>
      </table>
    </div>
    <div id="empty" class="empty" style="display:none">No cookies match your filters.</div>
    <div style="display:flex;gap:8px;margin-top:10px;flex-wrap:wrap">
      <button class="btn danger" id="deleteDomainBtn">Delete Cookies for Domain</button>
      <span class="muted" style="font-size:11px;align-self:center">Uses the current search domain or prompts for one.</span>
    </div>
  </div>

  <div class="card">
    <h2>Test Cookie</h2>
    <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:end">
      <label style="display:flex;flex-direction:column;gap:4px;font-size:11px;color:#9aa3b2">Name<input class="input-sm" id="testName" value="rhodium_test" style="width:180px"></label>
      <label style="display:flex;flex-direction:column;gap:4px;font-size:11px;color:#9aa3b2">Value<input class="input-sm" id="testValue" value="hello" style="width:180px"></label>
      <label style="display:flex;flex-direction:column;gap:4px;font-size:11px;color:#9aa3b2">Domain (optional)<input class="input-sm" id="testDomain" placeholder="example.com" style="width:160px"></label>
      <button class="btn primary" id="setTestBtn">Set Test Cookie</button>
      <button class="btn" id="refreshBtn2">Refresh Cookies</button>
    </div>
    <div class="muted" style="font-size:11px;margin-top:6px">Creates a cookie via the live <code>QWebEngineCookieStore.setCookie</code>. Refresh to see it.</div>
  </div>

</div>

<div class="modal" id="modal">
  <div class="modal-card">
    <h3 id="modalTitle">Cookie Details</h3>
    <div class="dl" id="modalDl"></div>
    <div class="details-actions">
      <button class="btn" id="toggleValue">Show Value</button>
      <button class="btn danger" id="modalDelete">Delete This Cookie</button>
      <button class="btn" id="modalClose">Close</button>
    </div>
  </div>
</div>

<script>
const COOKIES = {safe_cookies};
const DIAG = {safe_diag};

function esc(s){{return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;')}}
function fmtExp(c){{ if(c.is_session) return '— (Session)'; if(!c.expiration) return 'Unknown'; try{{ const d=new Date(c.expiration); if(isNaN(d)) return esc(c.expiration); return d.toLocaleString() }}catch(e){{return esc(c.expiration)}} }}
function sameSiteLabel(v){{ const m={{0:'Default',1:'None',2:'Lax',3:'Strict'}}; return m[v]!==undefined?m[v]:(v||'Unknown') }}

let currentModal = null;
let revealed = false;

function renderStatus(){{
  const row=document.getElementById('statusRow');
  const isPersistent = DIAG.is_persistent;
  const cls = isPersistent ? 'pill' : 'pill off';
  const dotLabel = isPersistent ? 'Profile: Persistent' : 'Profile: Session / Off-the-record';
  row.innerHTML = '<span class=\"'+cls+'\"><span class=\"dot\"></span><b>'+esc(dotLabel)+'</b></span>'
    + '<span class=\"pill\"><b>Storage Path:</b>&nbsp;<span class=\"mono\">'+esc(DIAG.storage_path||'Unknown')+'</span></span>'
    + '<span class=\"pill\"><b>Cookie Store:</b>&nbsp;'+(DIAG.cookie_connected?'Connected':'Not connected')+'</span>'
    + '<span class=\"pill\"><b>Total Cookies:</b>&nbsp;'+COOKIES.length+'</span>';
}}

function renderStats(){{
  const el=document.getElementById('statsCard');
  const total=COOKIES.length;
  const sess=COOKIES.filter(c=>c.is_session).length;
  const pers=total-sess;
  const sec=COOKIES.filter(c=>c.secure).length;
  el.innerHTML = '<h2>Overview</h2><div class=\"grid2\">'
    + '<div class=\"kv\"><div class=\"k\">Total Cookies</div><div class=\"v\">'+total+'</div></div>'
    + '<div class=\"kv\"><div class=\"k\">Persistent / Session</div><div class=\"v\">'+pers+' persistent · '+sess+' session</div></div>'
    + '<div class=\"kv\"><div class=\"k\">Secure</div><div class=\"v\">'+sec+' secure</div></div>'
    + '<div class=\"kv\"><div class=\"k\">Storage Path</div><div class=\"v mono\">'+esc(DIAG.storage_path||'Unknown')+'</div></div>'
    + '</div>';
}}

function renderDiagnostics(){{
  const g=document.getElementById('diagGrid');
  function kv(k,v){{return '<div class=\"kv\"><div class=\"k\">'+esc(k)+'</div><div class=\"v mono\">'+esc(v||'Unknown')+'</div></div>'}}
  g.innerHTML = kv('Profile type', DIAG.profile_type)
    + kv('Persistent storage path', DIAG.storage_path)
    + kv('Cache path', DIAG.cache_path)
    + kv('Cookie store', DIAG.cookie_connected?'Connected':'Not connected')
    + kv('Persistent cookies policy', DIAG.cookies_policy)
    + kv('Persistent permissions policy', DIAG.permissions_policy||'Not exposed by QtWebEngine');
  const raw=document.getElementById('rawBox');
  raw.textContent = JSON.stringify({{diagnostics:DIAG, cookie_count:COOKIES.length, sample: COOKIES.slice(0,3)}}, null, 2);
}}

let filtered = COOKIES.slice();
function applyFilters(){{
  const q=(document.getElementById('search').value||'').toLowerCase();
  const type=document.getElementById('typeFilter').value;
  const secOnly=document.getElementById('secureOnly').checked;
  const httpOnlyOnly=document.getElementById('httpOnlyOnly').checked;
  filtered = COOKIES.filter(c=>{{
    if(q && !( (c.name||'').toLowerCase().includes(q) || (c.domain||'').toLowerCase().includes(q) || (c.path||'').toLowerCase().includes(q) )) return false;
    if(type==='persistent' && c.is_session) return false;
    if(type==='session' && !c.is_session) return false;
    if(secOnly && !c.secure) return false;
    if(httpOnlyOnly && !c.httponly) return false;
    return true;
  }});
  renderTable();
}}

function renderTable(){{
  const tb=document.getElementById('tbody');
  const empty=document.getElementById('empty');
  tb.innerHTML='';
  if(!filtered.length){{ empty.style.display='block'; return }} else empty.style.display='none';
  for(let i=0;i<filtered.length;i++){{ const c=filtered[i];
    const tr=document.createElement('tr');
    tr.dataset.idx = COOKIES.indexOf(c);
    tr.innerHTML = '<td>'+esc(c.name)+'</td>'
      + '<td class=\"masked\">••••••••</td>'
      + '<td>'+esc(c.domain)+'</td>'
      + '<td>'+esc(c.path)+'</td>'
      + '<td>'+(c.is_session?'<span class=\"badge-yes\">YES</span>':'<span class=\"badge-no\">NO</span>')+'</td>'
      + '<td>'+(c.secure?'YES':'NO')+'</td>'
      + '<td>'+(c.httponly?'YES':'NO')+'</td>'
      + '<td>'+esc(c.samesite||'Unknown')+'</td>'
      + '<td>'+esc(fmtExp(c))+'</td>'
      + '<td><button class=\"btn\" data-del=\"'+COOKIES.indexOf(c)+'\">Delete</button></td>';
    tr.addEventListener('click', (e)=>{{ if(e.target.closest('button')) return; openModal(c); }});
    tb.appendChild(tr);
  }}
  tb.querySelectorAll('[data-del]').forEach(b=>{{ b.addEventListener('click', (e)=>{{ e.stopPropagation(); const idx=parseInt(b.dataset.del,10); const c=COOKIES[idx]; if(!c) return; if(!confirm('Delete cookie \"'+c.name+'\" for '+c.domain+' ?')) return; window.location.href='rhodium://cookie-debugger-delete?name='+encodeURIComponent(c.name)+'&domain='+encodeURIComponent(c.domain)+'&path='+encodeURIComponent(c.path); }}) }})
}}

function openModal(c){{
  currentModal=c; revealed=false;
  const modal=document.getElementById('modal');
  const dl=document.getElementById('modalDl');
  const title=document.getElementById('modalTitle');
  title.textContent = c.name + ' — ' + (c.is_session?'Session Cookie':'Persistent Cookie');
  title.style.color = c.is_session ? '#ff9c9c' : '#7ee8a6';
  function row(k,v){{return '<dt>'+esc(k)+'</dt><dd>'+esc(v)+'</dd>'}}
  dl.innerHTML = row('Name', c.name)
    + row('Value', '••••••••')
    + row('Domain', c.domain)
    + row('Path', c.path)
    + row('Session Cookie', c.is_session?'YES — session only':'NO — persistent')
    + row('Secure', c.secure?'YES':'NO')
    + row('HttpOnly', c.httponly?'YES':'NO')
    + row('SameSite', c.samesite||'Unknown')
    + row('Expiration', fmtExp(c))
    + row('Source', c.domain||'Unknown');
  document.getElementById('toggleValue').textContent='Show Value';
  modal.classList.add('open');
}}
function closeModal(){{ document.getElementById('modal').classList.remove('open'); currentModal=null; }}

document.getElementById('modalClose').addEventListener('click', closeModal);
document.getElementById('modal').addEventListener('click', (e)=>{{ if(e.target.id==='modal') closeModal(); }});
document.getElementById('toggleValue').addEventListener('click', ()=>{{
  if(!currentModal) return;
  const dd=document.querySelectorAll('#modalDl dd')[1];
  if(!revealed){{ dd.textContent=currentModal.value; document.getElementById('toggleValue').textContent='Hide Value'; revealed=true; }}
  else {{ dd.textContent='••••••••'; document.getElementById('toggleValue').textContent='Show Value'; revealed=false; }}
}});
document.getElementById('modalDelete').addEventListener('click', ()=>{{
  if(!currentModal) return;
  if(!confirm('Delete cookie \"'+currentModal.name+'\" for '+currentModal.domain+' ?')) return;
  window.location.href='rhodium://cookie-debugger-delete?name='+encodeURIComponent(currentModal.name)+'&domain='+encodeURIComponent(currentModal.domain)+'&path='+encodeURIComponent(currentModal.path);
}});

document.getElementById('search').addEventListener('input', applyFilters);
document.getElementById('typeFilter').addEventListener('change', applyFilters);
document.getElementById('secureOnly').addEventListener('change', applyFilters);
document.getElementById('httpOnlyOnly').addEventListener('change', applyFilters);
document.getElementById('clearFilter').addEventListener('click', ()=>{{ document.getElementById('search').value=''; document.getElementById('typeFilter').value='all'; document.getElementById('secureOnly').checked=false; document.getElementById('httpOnlyOnly').checked=false; applyFilters(); }});
document.getElementById('refreshBtn').addEventListener('click', ()=>{{ window.location.href='rhodium://cookie-debugger-refresh'; }});
document.getElementById('refreshBtn2').addEventListener('click', ()=>{{ window.location.href='rhodium://cookie-debugger-refresh'; }});
document.getElementById('deleteAllBtn').addEventListener('click', ()=>{{ if(!confirm('Delete all cookies from Rhodium?')) return; window.location.href='rhodium://cookie-debugger-delete-all'; }});
document.getElementById('deleteDomainBtn').addEventListener('click', ()=>{{ let d=(document.getElementById('search').value||'').trim(); if(!d || d.includes(' ')) d=prompt('Enter domain to clear (e.g. example.com):','')||''; if(!d) return; window.location.href='rhodium://cookie-debugger-delete-domain?domain='+encodeURIComponent(d); }});
document.getElementById('toggleRaw').addEventListener('click', ()=>{{ const w=document.getElementById('rawWrap'); const b=document.getElementById('toggleRaw'); if(w.style.display==='none'){{w.style.display='block';b.textContent='Hide Raw Debug Information'}} else {{w.style.display='none';b.textContent='Show Raw Debug Information'}} }});
document.getElementById('setTestBtn').addEventListener('click', ()=>{{ const n=document.getElementById('testName').value.trim()||'rhodium_test'; const v=document.getElementById('testValue').value; const d=document.getElementById('testDomain').value.trim(); window.location.href='rhodium://cookie-debugger-set-test?name='+encodeURIComponent(n)+'&value='+encodeURIComponent(v)+'&domain='+encodeURIComponent(d); }});

renderStatus(); renderStats(); renderDiagnostics(); applyFilters();
</script>
</body>
</html>"""


def get_bookmarks_page_html(bookmarks_json: str = "[]") -> str:
    """Generate the rhodium://bookmarks internal page.

    `bookmarks_json` is a JSON array of rows from the bookmark store.
    Each row: {"name", "url"} where url is the bookmark target.
    """
    safe_json = bookmarks_json.replace("</", "<\\/")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Bookmarks — Rhodium</title>
<style>
{css_vars()}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
    background: var(--bg_app); color: var(--text_primary);
    font-family: "Segoe UI", Inter, -apple-system, BlinkMacSystemFont, sans-serif;
    min-height: 100vh;
}}
.page {{ max-width: 920px; margin: 0 auto; padding: 36px 24px 56px; }}
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
.section {{ margin-bottom: 26px; }}
.section-title {{
    font-size: 11px; font-weight: 700; letter-spacing: .1em;
    text-transform: uppercase; color: var(--text_muted); margin: 18px 4px 10px;
}}
.list {{ display: flex; flex-direction: column; gap: 6px; }}
.item {{
    background: var(--bg_surface); border: 1px solid var(--border); border-radius: 12px;
    padding: 10px 14px; display: grid; grid-template-columns: 34px 1fr auto;
    gap: 12px; align-items: center; transition: border-color .15s, box-shadow .15s;
    cursor: pointer;
}}
.item:hover {{ border-color: var(--border_strong); box-shadow: var(--shadow_sm); }}
.fav-wrap {{
    width: 32px; height: 32px; border-radius: 9px; background: var(--bg_sunken);
    display: grid; place-items: center; overflow: hidden; font-size: 15px;
}}
.fav-wrap img {{ width: 22px; height: 22px; }}
.meta {{ min-width: 0; }}
.title {{
    font-size: 13px; font-weight: 600; color: var(--text_primary);
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}}
.sub {{ font-size: 11px; color: var(--text_secondary); margin-top: 2px;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.del {{
    background: var(--bg_sunken); color: var(--text_secondary); border: none; border-radius: 8px;
    padding: 6px 11px; font-size: 11px; cursor: pointer; opacity: 0; transition: opacity .15s, background .15s, color .15s;
}}
.item:hover .del {{ opacity: 1; }}
.del:hover {{ background: var(--danger_soft); color: var(--danger); }}
.empty {{ text-align: center; color: var(--text_muted); padding: 48px 20px; font-size: 13px; }}
.empty .big {{ font-size: 42px; opacity: .5; margin-bottom: 12px; }}
.empty .hint {{ margin-top: 6px; font-size: 12px; color: var(--text_muted); }}
</style>
</head>
<body>
<div class="page">
    <div class="header">
        <div class="heading">
            <div class="heading-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"
                     stroke-linecap="round" stroke-linejoin="round"><path d="M6 3h12v18l-6-4-6 4Z"/></svg>
            </div>
            <div>
                <h1>Bookmarks</h1>
                <div class="sub">Your saved places</div>
            </div>
        </div>
        <div class="header-actions">
            <input type="search" class="search" id="search" placeholder="Search bookmarks…">
        </div>
    </div>
    <div id="content"></div>
    <div class="empty" id="empty-msg" style="display:none">
        <div class="big">🔖</div>
        <div>No bookmarks yet</div>
        <div class="hint">Add a bookmark using the bookmark button or Ctrl+D</div>
    </div>
</div>
<script>
const ALL_BOOKMARKS = {safe_json};

function domainOf(url) {{
    try {{ return new URL(url).hostname; }} catch (e) {{ return ''; }}
}}
function escapeHtml(s) {{
    return String(s == null ? '' : s)
        .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
        .replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}}
function faviconOf(url) {{
    const dom = domainOf(url);
    if (dom) {{
        return '<img src="https://www.google.com/s2/favicons?sz=32&domain='
            + encodeURIComponent(dom)
            + '" onerror="this.style.display=&quot;none&quot;;this.parentNode.textContent=&quot;🌐&quot;">';
    }}
    return '🌐';
}}
function delHref(url) {{
    return 'rhodium://bookmark-action?action=delete&url=' + encodeURIComponent(url);
}}
function navigateHref(url) {{
    return 'rhodium://navigate?q=' + encodeURIComponent(url);
}}

function render() {{
    const q = document.getElementById('search').value.trim().toLowerCase();
    let items = ALL_BOOKMARKS;
    if (q) {{
        items = items.filter(b =>
            (b.name || '').toLowerCase().includes(q) ||
            (b.url || '').toLowerCase().includes(q)
        );
    }}
    const content = document.getElementById('content');
    content.innerHTML = '';
    if (items.length) {{
        const list = document.createElement('div');
        list.className = 'list';
        items.forEach(b => {{
            const title = b.name && b.name.trim() ? b.name : b.url;
            const url = b.url || '';
            list.innerHTML += '<div class="item" data-nav="' + navigateHref(url) + '">'
                + '<div class="fav-wrap">' + faviconOf(url) + '</div>'
                + '<div class="meta"><div class="title" title="' + escapeHtml(title) + '">' + escapeHtml(title) + '</div>'
                + '<div class="sub" title="' + escapeHtml(url) + '">' + escapeHtml(url) + '</div></div>'
                + '<button class="del" data-del="' + delHref(url) + '">Remove</button>'
                + '</div>';
        }});
        content.appendChild(list);
    }}
    document.getElementById('empty-msg').style.display = items.length ? 'none' : 'block';

    content.querySelectorAll('.item').forEach(el => {{
        el.addEventListener('click', e => {{
            if (e.target.closest('.del')) return;
            window.location.href = el.dataset.nav;
        }});
    }});
    content.querySelectorAll('.del').forEach(el => {{
        el.addEventListener('click', e => {{
            e.stopPropagation();
            window.location.href = el.dataset.del;
        }});
    }});
}}

document.getElementById('search').addEventListener('input', render);
render();
</script>
</body>
</html>"""
