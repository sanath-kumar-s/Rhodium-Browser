import base64
import html as html_module
import urllib.parse
import os
from urllib.parse import urlparse

def get_stylesheet() -> str:
    return """
        /* =========================================================
        RHODIUM — PROFESSIONAL DARK BROWSER UI
        ========================================================= */

        * {
            font-family: "Segoe UI", "Inter", Arial, sans-serif;
        }

        QMainWindow {
            background: #0b0d10;
            color: #e8eaed;
        }

        QWidget#BrowserRoot {
            background: #0b0d10;
        }

        QWidget#BrowserSurface {
            background: #0b0d10;
        }


        /* =========================================================
        NAVIGATION BAR
        ========================================================= */

        QToolBar#NavBar {
            background: #111318;

            border: none;
            border-bottom: 1px solid #20242b;

            padding: 5px 7px;

            spacing: 2px;

            min-height: 46px;
            max-height: 46px;
        }


        /* =========================================================
        NAVIGATION BUTTONS
        ========================================================= */

        QPushButton#NavBtn {
            background: transparent;

            border: none;
            border-radius: 8px;

            color: #9da4af;

            padding: 6px;

            min-width: 34px;
            min-height: 34px;
            max-width: 34px;
            max-height: 34px;
        }

        QPushButton#NavBtn:hover {
            background: #1c2027;
            color: #e7eaf0;
        }

        QPushButton#NavBtn:pressed {
            background: #272c34;
            color: #ffffff;
        }

        QPushButton#NavBtn:disabled {
            color: #4c525c;
        }


        /* =========================================================
        URL BAR
        ========================================================= */

        QLineEdit#UrlBar {
            background: #191c21;

            color: #e7e9ed;

            border: 1px solid #292e36;
            border-radius: 9px;

            padding: 7px 14px;

            font-size: 13px;

            selection-background-color: #355f98;
            selection-color: #ffffff;
        }

        QLineEdit#UrlBar:hover {
            background: #1c2026;
            border-color: #353b45;
        }

        QLineEdit#UrlBar:focus {
            background: #1b1f25;

            border: 1px solid #456b9f;

            selection-background-color: #365f98;
        }


        /* =========================================================
        BROWSER TABS
        ========================================================= */

        QTabWidget#BrowserTabs {
            background: #0b0d10;
            border: none;
        }

        QTabWidget#BrowserTabs::pane {
            border: none;
            background: #0b0d10;
            top: -1px;
        }

        QTabWidget#BrowserTabs::tab-bar {
            alignment: left;
            left: 0;
        }

        QTabBar#RhodiumTabBar {
            background: #0e1014;
            border: none;
            border-bottom: 1px solid #1c2129;
            padding: 6px 10px 0 10px;
            qproperty-drawBase: 0;
            min-height: 42px;
            max-height: 42px;
        }

        QTabBar#RhodiumTabBar::tab {
            background: #161920;
            color: #8b939f;
            border: 1px solid #232830;
            border-bottom: none;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
            padding: 0 12px 0 10px;
            margin-top: 3px;
            margin-right: 5px;
            min-width: 96px;
            max-width: 210px;
            min-height: 32px;
            max-height: 32px;
            font-size: 12px;
            font-weight: 500;
        }

        QTabBar#RhodiumTabBar::tab:hover {
            background: #1d222b;
            color: #c8ced8;
            border-color: #2d343f;
        }

        QTabBar#RhodiumTabBar::tab:selected {
            background: #0b0d10;
            color: #eef1f5;
            border-color: #2a313c;
            border-bottom: 2px solid #0b0d10;
            margin-top: 1px;
            min-height: 34px;
            max-height: 34px;
        }

        QTabBar#RhodiumTabBar::close-button {
            image: url(style/icons/close (2).png);
            width: 16px;
            height: 16px;
            subcontrol-position: right;
            margin-left: 6px;
            margin-right: 2px;
            border-radius: 4px;
            padding: 2px;
        }

        QTabBar#RhodiumTabBar::close-button:hover {
            background: #2a3039;
        }

        QTabBar#RhodiumTabBar::close-button:pressed {
            background: #353c47;
        }

        QTabBar#RhodiumTabBar QToolButton {
            background: #181c23;
            border: 1px solid #252b34;
            border-radius: 8px;
            color: #9aa3b0;
            margin: 6px 4px 8px 4px;
            padding: 4px 6px;
            min-width: 22px;
            max-width: 22px;
        }

        QTabBar#RhodiumTabBar QToolButton:hover {
            background: #242a33;
            color: #eef1f5;
            border-color: #333b47;
        }

        QToolButton#NewTabButton {
            background: #181c23;
            border: 1px solid #252b34;
            border-radius: 8px;
            padding: 6px;
            margin-left: 2px;
            margin-top: 6px;
            margin-right: 4px;
            color: #9aa3b0;
            min-width: 28px;
            max-width: 28px;
            min-height: 28px;
            max-height: 28px;
        }

        QToolButton#NewTabButton:hover {
            background: #242a33;
            color: #eef1f5;
            border-color: #333b47;
        }

        QToolButton#NewTabButton:pressed {
            background: #2d343f;
        }


        /* =========================================================
        STATUS BAR
        ========================================================= */

        QStatusBar {
            background: #111318;

            border-top: 1px solid #20242b;

            color: #707782;

            min-height: 22px;
            max-height: 22px;
        }

        QLabel#StatusLabel {
            color: #737a85;

            font-size: 11px;

            padding-left: 8px;
            padding-right: 8px;
        }


        /* =========================================================
        MENUS
        ========================================================= */

        QMenu {
            background: #181b20;

            color: #e3e6eb;

            border: 1px solid #30353d;
            border-radius: 9px;

            padding: 5px;

            font-size: 12px;
        }

        QMenu::item {
            padding: 8px 32px 8px 12px;

            border-radius: 6px;

            margin: 1px;
        }

        QMenu::item:selected {
            background: #272c34;
            color: #ffffff;
        }

        QMenu::separator {
            height: 1px;

            background: #2b3037;

            margin: 5px 8px;
        }

        QMenu::section {
            color: #747b86;

            font-size: 10px;

            padding: 6px 12px 4px;

            font-weight: 600;
        }

        QPushButton#WinMinBtn,
        QPushButton#WinMaxBtn,
        QPushButton#WinCloseBtn {
            border: none;
            background: transparent;
            color: #aaaaaa;
            font-size: 15px;
            border-radius: 5px;
        }

        QPushButton#WinMinBtn:hover,
        QPushButton#WinMaxBtn:hover {
            background: #2a2a2a;
            color: white;
        }

        QPushButton#WinCloseBtn:hover {
            background: #e81123;
            color: white;
        }

        QPushButton#WinMinBtn:pressed,
        QPushButton#WinMaxBtn:pressed,
        QPushButton#WinCloseBtn:pressed {
            background: #444444;
        }


        /* =========================================================
        DIALOGS
        ========================================================= */

        QDialog {
            background: #111318;
            color: #e1e4e8;
        }

        QLabel {
            color: #b9bec7;
        }

        QLabel#SettingsTitle {
            color: #f2f4f7;

            font-size: 18px;

            font-weight: 600;
        }


        /* =========================================================
        GENERAL INPUTS
        ========================================================= */

        QLineEdit {
            background: #181b21;

            color: #e1e4e8;

            border: 1px solid #2b2f36;

            border-radius: 7px;

            padding: 7px 10px;
        }

        QLineEdit:hover {
            border-color: #383d46;
        }

        QLineEdit:focus {
            border-color: #426cae;
        }


        /* =========================================================
        GENERAL BUTTONS
        ========================================================= */

        QPushButton {
            background: #1b1e24;

            color: #c6cad1;

            border: 1px solid #2b2f36;

            border-radius: 7px;

            padding: 7px 14px;

            font-size: 12px;
        }

        QPushButton:hover {
            background: #252930;

            color: #ffffff;

            border-color: #383d46;
        }

        QPushButton:pressed {
            background: #30353e;
        }

        QPushButton#PrimaryBtn {
            background: #315f9d;

            color: #ffffff;

            border: none;
        }

        QPushButton#PrimaryBtn:hover {
            background: #3b6fae;
        }


        /* =========================================================
        CHECKBOX
        ========================================================= */

        QCheckBox {
            color: #bfc4cc;

            spacing: 6px;
        }

        QCheckBox::indicator {
            width: 15px;
            height: 15px;

            border-radius: 4px;

            border: 1px solid #3a3f48;

            background: #181b21;
        }

        QCheckBox::indicator:checked {
            background: #426cae;

            border-color: #426cae;
        }


        /* =========================================================
        COMBO / SPIN
        ========================================================= */

        QSpinBox,
        QComboBox {
            background: #181b21;

            color: #e1e4e8;

            border: 1px solid #2b2f36;

            border-radius: 7px;

            padding: 6px 8px;
        }

        QSpinBox:focus,
        QComboBox:focus {
            border-color: #426cae;
        }


        /* =========================================================
        LIST
        ========================================================= */

        QListWidget {
            background: #181b21;

            color: #d0d4da;

            border: 1px solid #2b2f36;

            border-radius: 7px;

            padding: 4px;
        }

        QListWidget::item {
            padding: 6px;

            border-radius: 5px;
        }

        QListWidget::item:selected {
            background: #292f38;
        }


        /* =========================================================
        TEXT EDIT
        ========================================================= */

        QTextEdit {
            background: #181b21;

            color: #d0d4da;

            border: 1px solid #2b2f36;

            border-radius: 7px;
        }


        /* =========================================================
        FIND BAR
        ========================================================= */

        QFrame#FindBar {
            background: #15171c;

            border-top: 1px solid #292d34;

            max-height: 44px;
        }

        QLineEdit#FindInput {
            background: #1b1e24;

            border-radius: 7px;

            padding: 5px 10px;

            max-width: 320px;
        }

        QPushButton#FindClose {
            background: transparent;

            border: none;

            border-radius: 5px;
        }

        QPushButton#FindClose:hover {
            background: #252930;
        }
        """

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
    for s in shortcuts:
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
            <article class="shortcut-card" data-url="{url_attr}">
                <button type="button" class="shortcut-main" aria-label="Open {name}">
                    <span class="shortcut-icon">{icon_element}</span>
                    <span class="shortcut-label">{name}</span>
                </button>
                <div class="shortcut-actions">
                    <button type="button" class="shortcut-action edit" data-href="{edit_href}" title="Edit">Edit</button>
                    <button type="button" class="shortcut-action delete" data-href="{delete_href}" title="Remove">Remove</button>
                </div>
            </article>
        """

    shortcuts_html += """
        <button type="button" class="shortcut-card add" id="add-shortcut">
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

html, body {{
    width: 100%;
    height: 100%;
}}

body {{
    position: relative;
    overflow: hidden;
    color: #eef1f6;
    font-family: "Segoe UI", Inter, -apple-system, BlinkMacSystemFont, sans-serif;
    background: #07080b;
    user-select: none;
}}

.bg {{
    position: fixed;
    inset: 0;
    pointer-events: none;
    overflow: hidden;
}}

.bg-grid {{
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(rgba(255,255,255,.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,.025) 1px, transparent 1px);
    background-size: 56px 56px;
    mask-image: radial-gradient(circle at 50% 42%, black 0%, transparent 72%);
    opacity: .55;
}}

.bg-orb {{
    position: absolute;
    border-radius: 50%;
    filter: blur(80px);
    opacity: .55;
    animation: drift 18s ease-in-out infinite alternate;
}}

.bg-orb.one {{
    width: 420px;
    height: 420px;
    top: -120px;
    left: 18%;
    background: radial-gradient(circle, rgba(88, 118, 168, .35), transparent 70%);
}}

.bg-orb.two {{
    width: 360px;
    height: 360px;
    bottom: -80px;
    right: 12%;
    background: radial-gradient(circle, rgba(120, 132, 156, .22), transparent 70%);
    animation-delay: -6s;
}}

.bg-orb.three {{
    width: 280px;
    height: 280px;
    top: 38%;
    left: 58%;
    background: radial-gradient(circle, rgba(70, 107, 159, .18), transparent 70%);
    animation-delay: -12s;
}}

@keyframes drift {{
    from {{ transform: translate3d(0, 0, 0) scale(1); }}
    to   {{ transform: translate3d(24px, -18px, 0) scale(1.08); }}
}}

.page {{
    position: relative;
    z-index: 1;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 48px 24px 64px;
}}

.shell {{
    width: min(760px, calc(100vw - 48px));
    display: flex;
    flex-direction: column;
    align-items: center;
    animation: rise .55s cubic-bezier(.22, 1, .36, 1) both;
}}

@keyframes rise {{
    from {{ opacity: 0; transform: translateY(18px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}

.hero {{
    text-align: center;
    margin-bottom: 32px;
}}

.brand {{
    display: inline-flex;
    align-items: center;
    gap: 14px;
    padding: 10px 18px 10px 10px;
    border-radius: 999px;
    background: rgba(255,255,255,.03);
    border: 1px solid rgba(255,255,255,.06);
    backdrop-filter: blur(12px);
}}

.brand-mark {{
    width: 42px;
    height: 42px;
    display: grid;
    place-items: center;
    border-radius: 10px;
    background: linear-gradient(145deg, #2a3444, #171d28);
    border: 1px solid rgba(156, 183, 216, .28);
    box-shadow: inset 0 1px 0 rgba(255,255,255,.08), 0 10px 24px rgba(0,0,0,.28);
}}

.brand-mark svg {{
    width: 22px;
    height: 22px;
    stroke: #b8c9de;
}}

.brand-name {{
    font-size: 22px;
    font-weight: 600;
    letter-spacing: -.03em;
    color: #f0f3f7;
}}

.search-panel {{
    width: 100%;
}}

.search {{
    display: flex;
    align-items: center;
    height: 56px;
    padding: 0 18px;
    border-radius: 16px;
    background: rgba(18, 21, 27, .72);
    border: 1px solid rgba(255,255,255,.08);
    box-shadow:
        0 18px 40px rgba(0,0,0,.28),
        inset 0 1px 0 rgba(255,255,255,.04);
    backdrop-filter: blur(18px);
    transition: border-color .2s ease, box-shadow .2s ease, transform .2s ease;
}}

.search:hover {{
    border-color: rgba(255,255,255,.12);
}}

.search:focus-within {{
    border-color: rgba(126, 184, 255, .55);
    box-shadow:
        0 18px 40px rgba(0,0,0,.28),
        0 0 0 4px rgba(70, 107, 159, .14),
        inset 0 1px 0 rgba(255,255,255,.05);
    transform: translateY(-1px);
}}

.search-icon {{
    width: 20px;
    height: 20px;
    margin-right: 14px;
    color: #7d8796;
    flex-shrink: 0;
}}

.search input {{
    width: 100%;
    border: none;
    outline: none;
    background: transparent;
    color: #f3f5f8;
    font-size: 15px;
}}

.search input::placeholder {{
    color: #727b89;
}}

.search-hint {{
    margin-top: 10px;
    text-align: center;
    color: #5f6877;
    font-size: 12px;
}}

.shortcuts-section {{
    width: 100%;
    margin-top: 34px;
}}

.section-head {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 14px;
    padding: 0 4px;
}}

.section-title {{
    color: #8b95a5;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: .08em;
    text-transform: uppercase;
}}

.section-count {{
    color: #5d6674;
    font-size: 12px;
}}

.shortcuts {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(108px, 1fr));
    gap: 12px;
}}

.shortcut-card {{
    position: relative;
    border: none;
    background: transparent;
    padding: 0;
    text-align: center;
}}

.shortcut-main,
.shortcut-card.add {{
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    padding: 14px 10px 12px;
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,.06);
    background: rgba(255,255,255,.025);
    color: #9aa3b2;
    cursor: pointer;
    transition:
        transform .18s ease,
        border-color .18s ease,
        background .18s ease,
        color .18s ease,
        box-shadow .18s ease;
}}

.shortcut-card.add {{
    border-style: dashed;
    background: rgba(255,255,255,.015);
}}

.shortcut-main:hover,
.shortcut-card.add:hover {{
    transform: translateY(-3px);
    border-color: rgba(255,255,255,.12);
    background: rgba(255,255,255,.045);
    color: #d7dde7;
    box-shadow: 0 14px 28px rgba(0,0,0,.22);
}}

.shortcut-icon {{
    width: 52px;
    height: 52px;
    display: grid;
    place-items: center;
    border-radius: 14px;
    background: linear-gradient(180deg, rgba(255,255,255,.06), rgba(255,255,255,.02));
    border: 1px solid rgba(255,255,255,.07);
}}

.shortcut-icon svg {{
    width: 22px;
    height: 22px;
    stroke: #aeb7c4;
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
    line-height: 1.25;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}}

.shortcut-actions {{
    position: absolute;
    top: 8px;
    right: 8px;
    display: none;
    gap: 4px;
}}

.shortcut-card:hover .shortcut-actions {{
    display: flex;
}}

.shortcut-action {{
    border: 1px solid rgba(255,255,255,.08);
    background: rgba(12, 14, 18, .92);
    color: #b4bcc8;
    border-radius: 8px;
    padding: 3px 7px;
    font-size: 10px;
    cursor: pointer;
}}

.shortcut-action.delete {{
    color: #ff8f8f;
}}

.shortcut-action:hover {{
    background: rgba(255,255,255,.08);
}}

.footer {{
    margin-top: 36px;
    text-align: center;
    color: #4d5664;
    font-size: 11px;
    letter-spacing: .24em;
    text-transform: uppercase;
}}
</style>
</head>
<body>

<div class="bg" aria-hidden="true">
    <div class="bg-grid"></div>
    <div class="bg-orb one"></div>
    <div class="bg-orb two"></div>
    <div class="bg-orb three"></div>
</div>

<main class="page">
    <div class="shell">

        <header class="hero">
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
        }}
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

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        html,
        body {{
            width: 100%;
            height: 100%;
        }}

        body {{
            background:
                radial-gradient(
                    circle at 50% 38%,
                    rgba(55, 77, 110, 0.10) 0%,
                    rgba(15, 17, 21, 0.04) 28%,
                    transparent 52%
                ),
                #0b0c0f;

            color: #e7e9ed;

            font-family:
                "Segoe UI",
                Inter,
                -apple-system,
                BlinkMacSystemFont,
                sans-serif;

            display: flex;
            justify-content: center;
            align-items: center;

            height: 100vh;

            overflow: hidden;
            user-select: none;
        }}

        .container {{
            width: 520px;
            max-width: calc(100vw - 60px);

            display: flex;
            flex-direction: column;
            align-items: center;

            text-align: center;

            transform: translateY(-20px);
        }}

        /* =========================================================
           ICON
           ========================================================= */

        .icon-container {{
            width: 72px;
            height: 72px;

            display: flex;
            align-items: center;
            justify-content: center;

            border-radius: 18px;

            background: linear-gradient(
                145deg,
                #26384f,
                #172131
            );

            border: 1px solid #35485f;

            box-shadow:
                0 10px 30px rgba(0, 0, 0, .28);

            margin-bottom: 24px;
        }}

        .icon-container svg {{
            width: 34px;
            height: 34px;

            stroke: #9cb7d8;
        }}

        /* =========================================================
           TITLE
           ========================================================= */

        h1 {{
            color: #e9ebef;

            font-size: 24px;
            font-weight: 600;

            letter-spacing: -0.5px;

            margin-bottom: 10px;
        }}

        /* =========================================================
           DESCRIPTION
           ========================================================= */

        .description {{
            color: #858c97;

            font-size: 13px;
            line-height: 1.6;

            max-width: 420px;

            margin-bottom: 18px;
        }}

        /* =========================================================
           FAILED URL
           ========================================================= */

        .url {{
            width: 100%;
            max-width: 440px;

            background: #15171b;

            border: 1px solid #292e36;
            border-radius: 8px;

            padding: 10px 14px;

            color: #686f7a;

            font-size: 11px;

            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;

            margin-bottom: 24px;
        }}

        /* =========================================================
           BUTTONS
           ========================================================= */

        .buttons {{
            display: flex;
            align-items: center;
            justify-content: center;

            gap: 8px;
        }}

        button {{
            height: 36px;

            padding: 0 16px;

            border-radius: 7px;

            border: 1px solid #2b2f36;

            background: #1b1e24;

            color: #c6cad1;

            font-family: inherit;
            font-size: 12px;

            cursor: pointer;

            transition:
                background .15s ease,
                border-color .15s ease,
                color .15s ease;
        }}

        button:hover {{
            background: #252930;

            border-color: #383d46;

            color: #ffffff;
        }}

        button:active {{
            background: #30353e;
        }}

        .primary {{
            background: #315f9d;

            border-color: #315f9d;

            color: #ffffff;
        }}

        .primary:hover {{
            background: #3b6fae;

            border-color: #3b6fae;
        }}

        /* =========================================================
           FOOTER
           ========================================================= */

        .footer {{
            margin-top: 32px;

            color: #4f555e;

            font-size: 10px;

            letter-spacing: .2px;
        }}

    </style>
</head>

<body>

    <div class="container">

        <!-- OFFLINE ICON -->

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


        <!-- TITLE -->

        <h1>
            No Internet Connection
        </h1>


        <!-- DESCRIPTION -->

        <div class="description">
            Rhodium couldn't load this page.
            Check your internet connection and try again.
        </div>


        <!-- FAILED URL -->

        <div class="url" title="{failed_url_display}">
            {failed_url_display}
        </div>


        <!-- ACTION BUTTONS -->

        <div class="buttons">

            <button onclick="goHome()">
                Go Home
            </button>

            <button class="primary" onclick="retry()">
                Try Again
            </button>

        </div>


        <!-- FOOTER -->

        <div class="footer">
            RHODIUM
        </div>

    </div>


    <script>

        function retry() {{
            window.location.href =
                'rhodium://retry';
        }}


        function goHome() {{
            window.location.href =
                'rhodium://home';
        }}

    </script>

</body>
</html>"""
