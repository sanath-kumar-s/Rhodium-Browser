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
