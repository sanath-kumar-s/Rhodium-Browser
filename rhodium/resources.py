import base64
import html as html_module
import urllib.parse
import os
from urllib.parse import urlparse

def get_stylesheet() -> str:
    return """
        /* =========================================================
        RHODIUM — PROFESSIONAL PREMIUM DARK BROWSER UI
        ========================================================= */

        * {
            font-family: "Inter", "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif;
            font-size: 12px;
        }

        QMainWindow {
            background: #0B0D10;
            color: #E8ECF2;
        }

        QWidget#BrowserRoot {
            background: #0B0D10;
            border: 1px solid #252B34;
        }

        QWidget#BrowserSurface {
            background: #0B0D10;
        }


        /* =========================================================
        NAVIGATION BAR
        ========================================================= */

        QToolBar#NavBar {
            background: #12151A;
            border: none;
            border-bottom: 1px solid #252B34;
            padding: 4px 6px;
            spacing: 2px;
            min-height: 42px;
            max-height: 42px;
        }


        /* =========================================================
        NAVIGATION BUTTONS
        ========================================================= */

        QPushButton#NavBtn {
            background: transparent;
            border: none;
            border-radius: 6px;
            color: #9AA3B2;
            padding: 6px;
            min-width: 32px;
            min-height: 32px;
            max-width: 32px;
            max-height: 32px;
        }

        QPushButton#NavBtn:hover {
            background: #171C23;
            color: #E8ECF2;
        }

        QPushButton#NavBtn:pressed {
            background: #1B2028;
            color: #ffffff;
        }

        QPushButton#NavBtn:disabled {
            color: #687282;
        }


        /* =========================================================
        URL BAR
        ========================================================= */

        QLineEdit#UrlBar {
            background: #101318;
            color: #E8ECF2;
            border: 1px solid #252B34;
            border-radius: 9px;
            padding: 4px 10px;
            font-size: 13px;
            selection-background-color: #6EA8FF;
            selection-color: #0B0D10;
        }

        QLineEdit#UrlBar:hover {
            background: #171C23;
            border-color: #303846;
        }

        QLineEdit#UrlBar:focus {
            background: #171C23;
            border: 1px solid #6EA8FF;
            selection-background-color: #6EA8FF;
        }


        /* =========================================================
        BROWSER TABS
        ========================================================= */

        QWidget#BrowserTabs {
            background: #0E1115;
            border: none;
        }

        QWidget#TabStrip {
            background: #0E1115;
            border-bottom: 1px solid #252B34;
        }

        QTabBar#RhodiumTabBar {
            background: transparent;
            border: none;
            qproperty-drawBase: 0;
            min-height: 36px;
            max-height: 36px;
            font-size: 12px;
            font-weight: 500;
        }

        QTabBar#RhodiumTabBar::tab {
            background: transparent;
            color: #9AA3B2;
            border: none;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            border-bottom-left-radius: 8px;
            border-bottom-right-radius: 8px;
            padding: 0 8px;
            margin-top: 3px;
            margin-bottom: 3px;
            margin-right: 3px;
            min-width: 90px;
            max-width: 220px;
            min-height: 30px;
            max-height: 30px;
        }

        QTabBar#RhodiumTabBar::tab:hover {
            background: #161B21;
            color: #E8ECF2;
        }

        QTabBar#RhodiumTabBar::tab:selected {
            background: #1B2028;
            color: #E8ECF2;
        }

        QTabBar#RhodiumTabBar::close-button {
            image: url(style/icons/close (2).png);
            width: 14px;
            height: 14px;
            subcontrol-position: right;
            margin-left: 4px;
            margin-right: 2px;
            border-radius: 4px;
            padding: 2px;
        }

        QTabBar#RhodiumTabBar::close-button:hover {
            background: #303846;
        }

        QTabBar#RhodiumTabBar QToolButton {
            background: transparent;
            border: none;
            border-radius: 4px;
            color: #9AA3B2;
            margin: 4px 2px;
            min-width: 20px;
            max-width: 20px;
        }

        QTabBar#RhodiumTabBar QToolButton:hover {
            background: #171C23;
            color: #E8ECF2;
        }

        QToolButton#NewTabButton {
            background: transparent;
            border: none;
            border-radius: 6px;
            padding: 0;
            margin-top: 4px;
            margin-bottom: 4px;
            color: #9AA3B2;
        }

        QToolButton#NewTabButton:hover {
            background: #171C23;
        }

        QToolButton#NewTabButton:pressed {
            background: #1B2028;
        }


        /* =========================================================
        DOWNLOADS
        ========================================================= */

        QToolButton#DownloadButton {
            background: transparent;
            border: none;
            border-radius: 6px;
            padding: 0;
            margin: 0 2px;
        }

        QToolButton#DownloadButton:hover {
            background: #171C23;
        }

        QToolButton#DownloadButton:pressed {
            background: #1B2028;
        }

        QFrame#DownloadPopup {
            background: #101318;
            border: 1px solid #252B34;
            border-radius: 8px;
        }

        QFrame#DownloadPanel {
            background: #101318;
            border: 1px solid #252B34;
            border-radius: 8px;
        }

        QLabel#PopupHeader {
            color: #E8ECF2;
            font-size: 13px;
            font-weight: 600;
            padding: 10px 12px;
        }

        QFrame#PanelDivider {
            background: #252B34;
            border: none;
        }

        QFrame#DownloadPopupItem {
            background: #12151A;
            border: 1px solid #252B34;
            border-radius: 6px;
        }

        QFrame#DownloadPopupItem:hover {
            border-color: #303846;
        }

        QFrame#DownloadMenuRow {
            background: transparent;
            border: none;
            border-radius: 6px;
        }

        QFrame#DownloadMenuRow:hover {
            background: #171C23;
        }

        QLabel#DownloadItemIcon {
            font-size: 14px;
            background: #171C23;
            border-radius: 4px;
        }

        QLabel#DownloadItemName {
            color: #E8ECF2;
            font-size: 12px;
            font-weight: 600;
        }

        QLabel#DownloadItemStatus {
            color: #9AA3B2;
            font-size: 11px;
        }

        QLabel#DownloadItemSpeed {
            color: #687282;
            font-size: 11px;
        }

        QProgressBar#DownloadProgressBar {
            background: #171C23;
            border: none;
            border-radius: 2px;
        }

        QProgressBar#DownloadProgressBar::chunk {
            background: #6EA8FF;
            border-radius: 2px;
        }

        QToolButton#DownloadMiniBtn {
            background: #171C23;
            color: #9AA3B2;
            border: none;
            border-radius: 4px;
            font-size: 11px;
        }

        QToolButton#DownloadMiniBtn:hover {
            background: #1B2028;
            color: #E8ECF2;
        }

        QLabel#PanelFooter {
            color: #6EA8FF;
            font-size: 12px;
            font-weight: 600;
            padding: 10px;
            border-top: 1px solid #252B34;
        }

        QLabel#PanelFooter:hover {
            background: #171C23;
        }

        QLabel#DownloadEmpty {
            color: #687282;
            font-size: 12px;
            padding: 20px;
        }

        QScrollArea#DownloadScroll {
            background: transparent;
            border: none;
        }

        QFrame#DownloadPopup QScrollBar:vertical,
        QFrame#DownloadPanel QScrollBar:vertical {
            background: transparent;
            width: 6px;
            margin: 4px 2px;
        }

        QFrame#DownloadPopup QScrollBar::handle:vertical,
        QFrame#DownloadPanel QScrollBar::handle:vertical {
            background: #252B34;
            border-radius: 2px;
            min-height: 20px;
        }

        QFrame#DownloadPopup QScrollBar::handle:vertical:hover,
        QFrame#DownloadPanel QScrollBar::handle:vertical:hover {
            background: #303846;
        }


        /* =========================================================
        SUGGESTION POPUP
        ========================================================= */

        QFrame#SuggestionPopup {
            background: #101318;
            border: 1px solid #252B34;
            border-radius: 8px;
        }

        QListWidget#SuggestionList {
            background: transparent;
            border: none;
            outline: none;
        }

        QListWidget#SuggestionList::item {
            background: transparent;
            border-radius: 6px;
            margin: 1px 2px;
        }

        QListWidget#SuggestionList::item:hover {
            background: #171C23;
        }

        QListWidget#SuggestionList::item:selected {
            background: #1B2028;
        }

        QWidget#SuggestionRow {
            background: transparent;
        }

        QLabel#SuggestionPrimary {
            color: #E8ECF2;
            font-size: 12px;
            font-weight: 500;
            background: transparent;
        }

        QLabel#SuggestionSecondary {
            color: #9AA3B2;
            font-size: 11px;
            background: transparent;
        }

        QLabel#SuggestionIcon {
            background: transparent;
        }


        /* =========================================================
        STATUS BAR
        ========================================================= */

        QStatusBar {
            background: #12151A;
            border-top: 1px solid #252B34;
            color: #687282;
            min-height: 22px;
            max-height: 22px;
        }

        QLabel#StatusLabel {
            color: #687282;
            font-size: 11px;
            padding-left: 6px;
            padding-right: 6px;
        }


        /* =========================================================
        MENUS
        ========================================================= */

        QMenu {
            background: #101318;
            color: #E8ECF2;
            border: 1px solid #252B34;
            border-radius: 6px;
            padding: 4px;
            font-size: 12px;
        }

        QMenu::item {
            padding: 6px 28px 6px 12px;
            border-radius: 4px;
            margin: 1px;
        }

        QMenu::item:selected {
            background: #1B2028;
            color: #ffffff;
        }

        QMenu::separator {
            height: 1px;
            background: #252B34;
            margin: 4px 6px;
        }

        QMenu::section {
            color: #687282;
            font-size: 10px;
            padding: 4px 12px 2px;
            font-weight: 600;
        }

        QPushButton#WinMinBtn,
        QPushButton#WinMaxBtn,
        QPushButton#WinCloseBtn {
            border: none;
            background: transparent;
            color: #9AA3B2;
            font-size: 14px;
            border-radius: 4px;
        }

        QPushButton#WinMinBtn:hover,
        QPushButton#WinMaxBtn:hover {
            background: #171C23;
            color: #E8ECF2;
        }

        QPushButton#WinCloseBtn:hover {
            background: #E06C75;
            color: white;
        }

        QPushButton#WinMinBtn:pressed,
        QPushButton#WinMaxBtn:pressed,
        QPushButton#WinCloseBtn:pressed {
            background: #1B2028;
        }


        /* =========================================================
        DIALOGS
        ========================================================= */

        QDialog {
            background: #101318;
            color: #E8ECF2;
        }

        QLabel {
            color: #9AA3B2;
        }

        QLabel#SettingsTitle {
            color: #E8ECF2;
            font-size: 16px;
            font-weight: 600;
        }


        /* =========================================================
        GENERAL INPUTS
        ========================================================= */

        QLineEdit {
            background: #101318;
            color: #E8ECF2;
            border: 1px solid #252B34;
            border-radius: 6px;
            padding: 5px 8px;
        }

        QLineEdit:hover {
            border-color: #303846;
        }

        QLineEdit:focus {
            border-color: #6EA8FF;
        }


        /* =========================================================
        GENERAL BUTTONS
        ========================================================= */

        QPushButton {
            background: #171C23;
            color: #9AA3B2;
            border: 1px solid #252B34;
            border-radius: 6px;
            padding: 6px 12px;
            font-size: 12px;
        }

        QPushButton:hover {
            background: #1B2028;
            color: #E8ECF2;
            border-color: #303846;
        }

        QPushButton:pressed {
            background: #252B34;
        }

        QPushButton#PrimaryBtn {
            background: #6EA8FF;
            color: #0B0D10;
            font-weight: 600;
            border: none;
        }

        QPushButton#PrimaryBtn:hover {
            background: #82B5FF;
        }


        /* =========================================================
        CHECKBOX
        ========================================================= */

        QCheckBox {
            color: #9AA3B2;
            spacing: 6px;
        }

        QCheckBox::indicator {
            width: 14px;
            height: 14px;
            border-radius: 3px;
            border: 1px solid #252B34;
            background: #101318;
        }

        QCheckBox::indicator:checked {
            background: #6EA8FF;
            border-color: #6EA8FF;
        }


        /* =========================================================
        COMBO / SPIN
        ========================================================= */

        QSpinBox,
        QComboBox {
            background: #101318;
            color: #E8ECF2;
            border: 1px solid #252B34;
            border-radius: 6px;
            padding: 4px 6px;
        }

        QSpinBox:focus,
        QComboBox:focus {
            border-color: #6EA8FF;
        }


        /* =========================================================
        LIST
        ========================================================= */

        QListWidget {
            background: #101318;
            color: #E8ECF2;
            border: 1px solid #252B34;
            border-radius: 6px;
            padding: 4px;
        }

        QListWidget::item {
            padding: 4px;
            border-radius: 4px;
        }

        QListWidget::item:selected {
            background: #1B2028;
        }


        /* =========================================================
        TEXT EDIT
        ========================================================= */

        QTextEdit {
            background: #101318;
            color: #E8ECF2;
            border: 1px solid #252B34;
            border-radius: 6px;
        }


        /* =========================================================
        FIND BAR
        ========================================================= */

        QFrame#FindBar {
            background: #12151A;
            border-top: 1px solid #252B34;
            max-height: 40px;
        }

        QLineEdit#FindInput {
            background: #101318;
            border-radius: 6px;
            padding: 4px 8px;
            max-width: 280px;
        }

        QPushButton#FindClose {
            background: transparent;
            border: none;
            border-radius: 4px;
        }

        QPushButton#FindClose:hover {
            background: #171C23;
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
    background: #0B0D10;
}}

body {{
    color: #E8ECF2;
    font-family: "Inter", "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif;
    user-select: none;
    display: flex;
    align-items: center;
    justify-content: center;
}}

.page {{
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 32px 24px;
}}

.shell {{
    width: min(700px, 100%);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 32px;
    animation: rise .4s cubic-bezier(.22, 1, .36, 1) both;
}}

@keyframes rise {{
    from {{ opacity: 0; transform: translateY(12px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}

.hero {{
    text-align: center;
}}

.brand {{
    display: inline-flex;
    align-items: center;
    gap: 10px;
    padding: 6px 12px;
}}

.brand-mark {{
    width: 28px;
    height: 28px;
    display: grid;
    place-items: center;
    border-radius: 6px;
    background: #1B2028;
    border: 1px solid #303846;
}}

.brand-mark svg {{
    width: 16px;
    height: 16px;
    stroke: #6EA8FF;
}}

.brand-name {{
    font-size: 22px;
    font-weight: 600;
    letter-spacing: -.02em;
    color: #E8ECF2;
}}

.search-panel {{
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 8px;
}}

.search {{
    display: flex;
    align-items: center;
    height: 52px;
    padding: 0 16px;
    border-radius: 12px;
    background: #101318;
    border: 1px solid #252B34;
    transition: border-color .15s ease, background .15s ease;
}}

.search:hover {{
    background: #171C23;
    border-color: #303846;
}}

.search:focus-within {{
    background: #171C23;
    border-color: #6EA8FF;
}}

.search-icon {{
    width: 18px;
    height: 18px;
    margin-right: 12px;
    color: #9AA3B2;
    flex-shrink: 0;
}}

.search input {{
    width: 100%;
    border: none;
    outline: none;
    background: transparent;
    color: #E8ECF2;
    font-size: 14px;
}}

.search input::placeholder {{
    color: #687282;
}}

.search-hint {{
    text-align: center;
    color: #687282;
    font-size: 11px;
}}

.shortcuts-section {{
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 12px;
}}

.section-head {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 2px;
}}

.section-title {{
    color: #9AA3B2;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: .05em;
    text-transform: uppercase;
}}

.section-count {{
    color: #687282;
    font-size: 11px;
}}

.shortcuts {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(115px, 1fr));
    gap: 12px;
    width: 100%;
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
    height: 98px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 10px;
    border-radius: 8px;
    border: 1px solid #252B34;
    background: #101318;
    color: #9AA3B2;
    cursor: pointer;
    transition: border-color .15s, background .15s, color .15s;
}}

.shortcut-card.add {{
    border-style: dashed;
}}

.shortcut-main:hover,
.shortcut-card.add:hover {{
    border-color: #303846;
    background: #171C23;
    color: #E8ECF2;
}}

.shortcut-icon {{
    width: 40px;
    height: 40px;
    display: grid;
    place-items: center;
    border-radius: 6px;
    background: #171C23;
    border: 1px solid #252B34;
}}

.shortcut-icon svg {{
    width: 18px;
    height: 18px;
    stroke: #9AA3B2;
}}

.shortcut-favicon {{
    width: 20px;
    height: 20px;
    border-radius: 4px;
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
    top: 4px;
    right: 4px;
    display: none;
    gap: 4px;
}}

.shortcut-card:hover .shortcut-actions {{
    display: flex;
}}

.shortcut-action {{
    border: 1px solid #252B34;
    background: #0B0D10;
    color: #9AA3B2;
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 10px;
    cursor: pointer;
}}

.shortcut-action.delete {{
    color: #E06C75;
}}

.shortcut-action:hover {{
    background: #171C23;
    color: #E8ECF2;
}}

.footer {{
    text-align: center;
    color: #687282;
    font-size: 11px;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 16px;
}}
</style>
</head>
<body>

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

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        html,
        body {{
            width: 100%;
            height: 100%;
            background: #0B0D10;
        }}

        body {{
            color: #E8ECF2;
            font-family: "Inter", "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            overflow: hidden;
            user-select: none;
        }}

        .container {{
            width: 480px;
            max-width: calc(100vw - 40px);
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
        }}

        .icon-container {{
            width: 60px;
            height: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 12px;
            background: #101318;
            border: 1px solid #252B34;
            margin-bottom: 20px;
        }}

        .icon-container svg {{
            width: 28px;
            height: 28px;
            stroke: #6EA8FF;
        }}

        h1 {{
            color: #E8ECF2;
            font-size: 20px;
            font-weight: 600;
            letter-spacing: -0.3px;
            margin-bottom: 8px;
        }}

        .description {{
            color: #9AA3B2;
            font-size: 12px;
            line-height: 1.5;
            max-width: 380px;
            margin-bottom: 16px;
        }}

        .url {{
            width: 100%;
            max-width: 380px;
            background: #101318;
            border: 1px solid #252B34;
            border-radius: 6px;
            padding: 8px 12px;
            color: #687282;
            font-size: 11px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            margin-bottom: 20px;
        }}

        .buttons {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }}

        button {{
            height: 34px;
            padding: 0 14px;
            border-radius: 6px;
            border: 1px solid #252B34;
            background: #171C23;
            color: #9AA3B2;
            font-family: inherit;
            font-size: 12px;
            cursor: pointer;
            transition: background .15s, border-color .15s, color .15s;
        }}

        button:hover {{
            background: #1B2028;
            border-color: #303846;
            color: #E8ECF2;
        }}

        .primary {{
            background: #6EA8FF;
            border-color: #6EA8FF;
            color: #0B0D10;
            font-weight: 600;
        }}

        .primary:hover {{
            background: #82B5FF;
            border-color: #82B5FF;
            color: #0B0D10;
        }}

        .footer {{
            margin-top: 28px;
            color: #687282;
            font-size: 10px;
            letter-spacing: 1px;
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
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
    background: #0b0d10;
    color: #e8eaed;
    font-family: "Segoe UI", Inter, -apple-system, BlinkMacSystemFont, sans-serif;
    min-height: 100vh;
}}
.page {{ max-width: 920px; margin: 0 auto; padding: 32px 24px 48px; }}
.header {{
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 24px; gap: 16px; flex-wrap: wrap;
}}
.header h1 {{ font-size: 24px; font-weight: 600; letter-spacing: -.02em; }}
.header-actions {{ display: flex; gap: 10px; align-items: center; flex: 1; justify-content: flex-end; }}
.search {{
    background: #181b21; border: 1px solid #2b2f36; border-radius: 9px;
    color: #e1e4e8; padding: 8px 12px; font-size: 13px; width: min(280px, 100%);
    outline: none;
}}
.search:focus {{ border-color: #426cae; }}
.btn {{
    background: #1b1e24; color: #c6cad1; border: 1px solid #2b2f36;
    border-radius: 7px; padding: 8px 14px; font-size: 12px; cursor: pointer;
}}
.btn:hover {{ background: #252930; color: #fff; }}
.btn-danger:hover {{ background: #4a2020; border-color: #6b3030; }}
.section {{ margin-bottom: 28px; }}
.section-title {{
    font-size: 11px; font-weight: 600; letter-spacing: .08em;
    text-transform: uppercase; color: #747b86; margin-bottom: 10px;
}}
.list {{ display: flex; flex-direction: column; gap: 8px; }}
.item {{
    background: #14171d; border: 1px solid #252b34; border-radius: 10px;
    padding: 14px 16px; display: grid; grid-template-columns: 36px 1fr auto;
    gap: 12px; align-items: start; transition: border-color .15s;
}}
.item:hover {{ border-color: #353d49; }}
.item.executable {{ border-left: 3px solid #e8a045; }}
.icon {{
    width: 32px; height: 32px; border-radius: 8px;
    background: #222730; display: grid; place-items: center; font-size: 16px;
}}
.meta {{ min-width: 0; }}
.name {{
    font-size: 13px; font-weight: 600; color: #eef1f5;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}}
.status {{ font-size: 11px; color: #8b939f; margin-top: 3px; }}
.details {{ font-size: 10px; color: #636b78; margin-top: 4px; word-break: break-all; }}
.progress-wrap {{ margin-top: 8px; }}
.progress {{
    height: 4px; background: #222730; border-radius: 2px; overflow: hidden;
}}
.progress-bar {{
    height: 100%; background: #4c8dff; border-radius: 2px;
    transition: width .2s ease;
}}
.progress-text {{ font-size: 10px; color: #727a87; margin-top: 4px; }}
.actions {{ display: flex; gap: 6px; flex-wrap: wrap; justify-content: flex-end; }}
.action {{
    background: #242932; color: #d5dae3; border: none; border-radius: 6px;
    padding: 5px 10px; font-size: 11px; cursor: pointer;
}}
.action:hover {{ background: #2e3540; color: #fff; }}
.action.primary {{ background: #315f9d; color: #fff; }}
.action.primary:hover {{ background: #3b6fae; }}
.empty {{
    text-align: center; color: #636b78; padding: 40px 20px; font-size: 13px;
}}
</style>
</head>
<body>
<div class="page">
    <div class="header">
        <h1>Downloads</h1>
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
        <div class="empty" id="empty-msg" style="display:none">No downloads yet</div>
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
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{
    background: #0b0d10; color: #e8eaed;
    font-family: "Segoe UI", Inter, -apple-system, BlinkMacSystemFont, sans-serif;
    min-height: 100vh;
}}
.page {{ max-width: 920px; margin: 0 auto; padding: 32px 24px 48px; }}
.header {{
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 24px; gap: 16px; flex-wrap: wrap;
}}
.header h1 {{ font-size: 24px; font-weight: 600; letter-spacing: -.02em; }}
.header-actions {{ display: flex; gap: 10px; align-items: center; flex: 1; justify-content: flex-end; position: relative; }}
.search {{
    background: #181b21; border: 1px solid #2b2f36; border-radius: 9px;
    color: #e1e4e8; padding: 8px 12px; font-size: 13px; width: min(280px, 100%);
    outline: none;
}}
.search:focus {{ border-color: #426cae; }}
.btn {{
    background: #1b1e24; color: #c6cad1; border: 1px solid #2b2f36;
    border-radius: 7px; padding: 8px 14px; font-size: 12px; cursor: pointer;
}}
.btn:hover {{ background: #252930; color: #fff; }}
.btn-danger:hover {{ background: #4a2020; border-color: #6b3030; }}
.clear-menu {{
    position: absolute; top: 42px; right: 0; z-index: 20;
    background: #161a20; border: 1px solid #2b2f36; border-radius: 10px;
    padding: 6px; min-width: 200px; box-shadow: 0 12px 30px rgba(0,0,0,.5);
    display: none;
}}
.clear-menu.open {{ display: block; }}
.clear-menu button {{
    display: block; width: 100%; text-align: left; background: none; border: none;
    color: #d5dae3; padding: 9px 12px; font-size: 12.5px; border-radius: 7px; cursor: pointer;
}}
.clear-menu button:hover {{ background: #232831; color: #fff; }}
.clear-menu button.danger:hover {{ background: #3a1c1c; color: #ff9c9c; }}
.section {{ margin-bottom: 26px; }}
.section-title {{
    font-size: 11px; font-weight: 600; letter-spacing: .08em;
    text-transform: uppercase; color: #747b86; margin: 18px 4px 10px;
}}
.list {{ display: flex; flex-direction: column; gap: 6px; }}
.item {{
    background: #14171d; border: 1px solid #252b34; border-radius: 10px;
    padding: 10px 12px; display: grid; grid-template-columns: 30px 1fr auto;
    gap: 12px; align-items: center; transition: border-color .15s, background .15s;
    cursor: pointer;
}}
.item:hover {{ border-color: #353d49; background: #171b22; }}
.fav-wrap {{
    width: 28px; height: 28px; border-radius: 7px; background: #222730;
    display: grid; place-items: center; overflow: hidden; font-size: 14px;
}}
.fav-wrap img {{ width: 20px; height: 20px; }}
.meta {{ min-width: 0; }}
.title {{
    font-size: 13px; font-weight: 600; color: #eef1f5;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}}
.sub {{ font-size: 11px; color: #8b939f; margin-top: 2px;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.time {{ font-size: 11px; color: #6f7785; white-space: nowrap; padding-right: 4px; }}
.del {{
    background: #242932; color: #d5dae3; border: none; border-radius: 6px;
    padding: 6px 10px; font-size: 11px; cursor: pointer; opacity: 0; transition: opacity .15s;
}}
.item:hover .del {{ opacity: 1; }}
.del:hover {{ background: #4a2020; color: #ff9c9c; }}
.empty {{ text-align: center; color: #636b78; padding: 48px 20px; font-size: 13px; }}
.empty .big {{ font-size: 40px; opacity: .5; margin-bottom: 10px; }}
</style>
</head>
<body>
<div class="page">
    <div class="header">
        <h1>History</h1>
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
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#0b0d10;color:#e8eaed;font-family:"Segoe UI",Inter,-apple-system,BlinkMacSystemFont,sans-serif;min-height:100vh}}
.page{{max-width:1100px;margin:0 auto;padding:28px 24px 48px}}
.header{{display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;margin-bottom:20px}}
.header h1{{font-size:22px;font-weight:700;letter-spacing:-.02em;display:flex;align-items:center;gap:10px}}
.header h1 span.badge{{font-size:11px;font-weight:600;letter-spacing:.06em;padding:4px 8px;border-radius:999px;background:#14171d;border:1px solid #252b34;color:#9aa3b2}}
.sub{{color:#8b939f;font-size:12px;margin-top:4px;max-width:720px;line-height:1.5}}
.status-row{{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-top:10px}}
.pill{{display:inline-flex;align-items:center;gap:6px;background:#14171d;border:1px solid #252b34;border-radius:999px;padding:6px 10px;font-size:11px;color:#c6cad1}}
.pill .dot{{width:8px;height:8px;border-radius:999px;background:#3dd68c;box-shadow:0 0 0 4px rgba(61,214,140,.15)}}
.pill.off .dot{{background:#e06c75;box-shadow:0 0 0 4px rgba(224,108,117,.15)}}
.pill b{{color:#eef1f5;font-weight:600}}
.card{{background:#14171d;border:1px solid #252b34;border-radius:12px;padding:14px 16px;margin-bottom:14px}}
.card h2{{font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#8b939f;margin-bottom:10px}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:10px}}
@media(max-width:760px){{.grid2{{grid-template-columns:1fr}}}}
.kv{{background:#0f1217;border:1px solid #232831;border-radius:8px;padding:10px 12px}}
.kv .k{{font-size:10px;letter-spacing:.07em;text-transform:uppercase;color:#6f7785;margin-bottom:4px}}
.kv .v{{font-size:12px;color:#d5dae3;word-break:break-all}}
.kv .v.mono{{font-family:ui-monospace,Consolas,monospace;font-size:11px}}
.toolbar{{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-bottom:10px}}
.toolbar .left{{display:flex;gap:8px;align-items:center;flex-wrap:wrap;flex:1}}
.search{{background:#0f1217;border:1px solid #2b2f36;border-radius:9px;color:#e1e4e8;padding:9px 12px;font-size:12.5px;width:min(360px,100%);outline:none}}
.search:focus{{border-color:#426cae}}
.select, .input-sm{{background:#0f1217;border:1px solid #2b2f36;border-radius:7px;color:#d5dae3;padding:8px 10px;font-size:12px;outline:none}}
.select:focus,.input-sm:focus{{border-color:#426cae}}
.btn{{background:#1b1e24;color:#c6cad1;border:1px solid #2b2f36;border-radius:7px;padding:8px 12px;font-size:12px;cursor:pointer;display:inline-flex;align-items:center;gap:6px}}
.btn:hover{{background:#252930;color:#fff}}
.btn.primary{{background:#315f9d;color:#fff;border-color:#315f9d}}
.btn.primary:hover{{background:#3b6fae}}
.btn.danger{{background:#2a1515;color:#ff9c9c;border-color:#4a2020}}
.btn.danger:hover{{background:#4a2020}}
.table-wrap{{overflow:auto;border:1px solid #252b34;border-radius:10px;background:#0f1217}}
table{{width:100%;border-collapse:collapse;min-width:860px}}
thead th{{text-align:left;font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:#747b86;background:#11141a;padding:10px 10px;border-bottom:1px solid #252b34;position:sticky;top:0}}
tbody td{{padding:9px 10px;border-bottom:1px solid #1b1f27;font-size:12px;color:#d5dae3;vertical-align:top;max-width:240px;word-break:break-all}}
tbody tr{{cursor:pointer}}
tbody tr:hover{{background:#171b22}}
.badge-yes{{background:#16301f;color:#7ee8a6;border:1px solid #1f4d2e;padding:2px 6px;border-radius:999px;font-size:10px;font-weight:700}}
.badge-no{{background:#1e232e;color:#8aa0c8;border:1px solid #2b3446;padding:2px 6px;border-radius:999px;font-size:10px;font-weight:700}}
.muted{{color:#6f7785}}
.masked{{letter-spacing:2px}}
.empty{{text-align:center;color:#636b78;padding:32px 16px;font-size:13px}}
.modal{{position:fixed;inset:0;background:rgba(0,0,0,.55);display:none;align-items:center;justify-content:center;padding:20px;z-index:50}}
.modal.open{{display:flex}}
.modal-card{{background:#14171d;border:1px solid #2b3446;border-radius:12px;max-width:620px;width:100%;padding:16px;max-height:85vh;overflow:auto}}
.modal-card h3{{font-size:14px;margin-bottom:8px}}
.dl{{display:grid;grid-template-columns:140px 1fr;gap:8px;font-size:12px;margin-top:10px}}
.dl dt{{color:#8b939f}}
.dl dd{{color:#eef1f5;word-break:break-all;font-family:ui-monospace,Consolas,monospace;font-size:11px}}
.details-actions{{display:flex;gap:8px;margin-top:12px;flex-wrap:wrap}}
.chk{{display:inline-flex;align-items:center;gap:6px;font-size:11px;color:#9aa3b2}}
.raw{{background:#0f1217;border:1px solid #232831;border-radius:8px;padding:10px;font-family:ui-monospace,Consolas,monospace;font-size:11px;white-space:pre-wrap;word-break:break-all;color:#9aa3b2;max-height:260px;overflow:auto}}
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
