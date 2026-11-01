"""Generator for Rhodium's internal ``rhodium://settings`` page.

The page is rendered as a self-contained HTML document (mirroring the design
language of ``rhodium://home``) with a left navigation sidebar, a category
content area and a live search filter.  Every control posts its change back to
Python through ``rhodium://settings-*`` routes handled by
:class:`AdvancedBrowser`.  The service is the single source of truth — this
page never stores settings itself.
"""

import html as html_module
import json
from urllib.parse import quote

from rhodium.theme import css_vars

_CATEGORIES = [
    ("general", "General", "General startup, homepage, theme and display preferences."),
    ("search", "Search Engine", "Choose your default search engine and manage custom engines."),
    ("privacy", "Privacy & Security", "Browsing data, permissions and security preferences."),
    ("cookies", "Cookies", "View and manage cookies stored by websites."),
    ("downloads", "Downloads", "Where files are saved and how downloads behave."),
    ("bookmarks", "Bookmarks", "Import, export and manage your bookmarks."),
    ("history", "History", "View and clear your browsing history."),
    ("appearance", "Appearance", "Theme, accent colour, toolbar and tab look."),
    ("tabs", "Tabs & Startup", "Tab behaviour and session restoration."),
    ("permissions", "Permissions", "Site permissions for camera, microphone, location and more."),
    ("passwords", "Password Manager", "Password management (coming soon)."),
]


def _es(text) -> str:
    return html_module.escape(str(text))


def _q(url) -> str:
    return html_module.escape(url, quote=True)


def _toggle(key, label, value, cat, desc="", disabled=False):
    checked = ' checked' if value else ''
    d = ' disabled' if disabled else ''
    desc_html = f'<div class="ctl-desc">{_es(desc)}</div>' if desc else ''
    return f"""
    <div class="ctl-row">
        <div class="ctl-info">
            <div class="ctl-label">{_es(label)}</div>
            {desc_html}
        </div>
        <label class="switch">
            <input type="checkbox" data-set="{_es(key)}" data-cat="{_es(cat)}"{checked}{d}>
            <span class="slider"></span>
        </label>
    </div>
    """


def _select(key, label, options, value, cat, desc="", disabled=False):
    d = ' disabled' if disabled else ''
    opts = ""
    for opt_value, opt_label in options:
        sel = ' selected' if str(opt_value) == str(value) else ''
        opts += f'<option value="{_es(opt_value)}"{sel}>{_es(opt_label)}</option>'
    desc_html = f'<div class="ctl-desc">{_es(desc)}</div>' if desc else ''
    return f"""
    <div class="ctl-row">
        <div class="ctl-info">
            <div class="ctl-label">{_es(label)}</div>
            {desc_html}
        </div>
        <select class="ctl-select" data-set="{_es(key)}" data-cat="{_es(cat)}"{d}>{opts}</select>
    </div>
    """


def _radio(key, label, name, options, value, cat, desc="", disabled=False):
    d = ' disabled' if disabled else ''
    radios = ""
    for opt_value, opt_label in options:
        checked = ' checked' if str(opt_value) == str(value) else ''
        radios += f"""
        <label class="radio">
            <input type="radio" name="{_es(name)}" value="{_es(opt_value)}"
                   data-set="{_es(key)}" data-cat="{_es(cat)}"{checked}{d}>
            <span class="radio-mark"></span>
            <span>{_es(opt_label)}</span>
        </label>
        """
    desc_html = f'<div class="ctl-desc">{_es(desc)}</div>' if desc else ''
    return f"""
    <div class="ctl-row col">
        <div class="ctl-info">
            <div class="ctl-label">{_es(label)}</div>
            {desc_html}
        </div>
        <div class="radio-group">{radios}</div>
    </div>
    """


def _text(key, label, value, cat, placeholder="", desc=""):
    desc_html = f'<div class="ctl-desc">{_es(desc)}</div>' if desc else ''
    return f"""
    <div class="ctl-row">
        <div class="ctl-info">
            <div class="ctl-label">{_es(label)}</div>
            {desc_html}
        </div>
        <input type="text" class="ctl-input" value="{_es(value)}"
               placeholder="{_es(placeholder)}" data-set="{_es(key)}" data-cat="{_es(cat)}">
    </div>
    """


def _button(text, route, cls="btn", method="js", confirm=""):
    c = f' data-confirm="{_es(confirm)}"' if confirm else ''
    if method == "js":
        return f'<button type="button" class="{cls}" data-route="{_q(route)}"{c}>{_es(text)}</button>'
    return f'<button type="button" class="{cls}" data-route="{_q(route)}"{c}>{_es(text)}</button>'


def _section_title(title, sub=""):
    sub_html = f'<div class="sec-sub">{_es(sub)}</div>' if sub else ''
    return f'<div class="sec-head"><div class="sec-title">{_es(title)}</div>{sub_html}</div>'


def _general(payload):
    s = payload["settings"]
    cat = "general"
    theme_opt = [("light", "Light"), ("dark", "Dark"), ("system", "System")]
    startup_opt = [("new_tab", "Open the new tab page"), ("continue", "Continue where you left off")]
    font_opt = [("small", "Small"), ("medium", "Medium"), ("large", "Large")]
    html = ""
    html += _section_title("Startup", "What Rhodium shows when it opens.")
    html += _radio("general.startup_mode", "On startup", "startup", startup_opt,
                   s.get("general.startup_mode", "new_tab"), cat)
    html += _select("general.newtab_page", "Default new-tab page",
                    [("about:home", "Rhodium Home"), ("about:blank", "Blank page")],
                    s.get("general.newtab_page", "about:home"), cat)
    html += _text("general.homepage", "Homepage", s.get("general.homepage", "about:home"),
                  cat, placeholder="about:home", desc="The page opened by the Home button and when opening a new window.")
    html += "<div class='sec-divider'></div>"
    html += _section_title("Appearance defaults", "Theme and display defaults for this browser.")
    html += _radio("general.theme", "Theme", "theme", theme_opt, s.get("general.theme", "light"), cat)
    html += _radio("general.font_size", "Font size", "font", font_opt,
                   s.get("general.font_size", "medium"), cat)
    html += _text("general.zoom", "Default zoom (%)", s.get("general.zoom", 100), cat,
                  placeholder="100")
    html += _select("general.language", "Language",
                    [("en", "English"), ("es", "Español"), ("fr", "Français"),
                     ("de", "Deutsch"), ("hi", "हिन्दी"), ("zh", "中文")],
                    s.get("general.language", "en"), cat, desc="Used where Rhodium supports localization.")
    html += "<div class='sec-divider'></div>"
    html += _button("Restore all settings", "rhodium://settings-reset?cat=general",
                    "btn danger", confirm="Reset all settings to their defaults?")
    return html


def _search_engine(payload):
    s = payload["settings"]
    engines = payload.get("engines", [])
    default_id = s.get("search.default_engine", "google")
    cat = "search"
    html = ""
    html += _section_title("Default search engine", "Searches from the address bar and new tab page use this engine.")
    rows = ""
    for e in engines:
        eid = e.get("id")
        is_default = eid == default_id
        custom = str(eid).startswith("custom")
        name = e.get("name", "Unnamed")
        keyword = e.get("keyword", "")
        kw = f'<span class="kw">/{_es(keyword)}</span>' if keyword else ''
        actions = ""
        if custom:
            actions += f'<button class="btn mini" data-route="rhodium://settings-search-edit?cat=search&amp;id={_q(eid)}&amp;name={_q(name)}&amp;url={_q(e.get("search_url",""))}&amp;suggest={_q(e.get("suggest_url",""))}&amp;keyword={_q(keyword)}">Edit</button>'
            actions += f'<button class="btn mini danger" data-route="rhodium://settings-search-delete?cat=search&amp;id={_q(eid)}" data-confirm="Delete this search engine?">Delete</button>'
        checked = " checked" if is_default else ""
        radio = f'<label class="radio engine-radio"><input type="radio" name="engine" value="{_es(eid)}" data-set="search.default_engine" data-cat="search"{checked}><span class="radio-mark"></span></label>'
        rows += f"""
        <div class="engine-row">
            {radio}
            <div class="engine-info">
                <div class="engine-name">{_es(name)} {kw}</div>
                <div class="engine-url">{_es(e.get("search_url",""))}</div>
            </div>
            <div class="engine-actions">{actions}</div>
        </div>
        """
    html += f'<div class="engine-list">{rows}</div>'
    html += "<div class='sec-divider'></div>"
    html += _section_title("Search suggestions", "Control suggestion sources.")
    html += _toggle("search.suggestions_enabled", "Search suggestions",
                    s.get("search.suggestions_enabled", True), cat,
                    desc="Fetch suggestions from your default engine when typing.")
    html += _toggle("search.address_bar_suggestions", "Address bar suggestions",
                    s.get("search.address_bar_suggestions", True), cat,
                    desc="Suggest matching history, bookmarks and searches in the address bar.")
    html += "<div class='sec-divider'></div>"
    html += _section_title("Custom search engines", "Add your own search engine using a URL template with {searchTerms}.")
    html += _add_engine_form()
    html += "<div class='sec-divider'></div>"
    html += _button("Restore default search engines", "rhodium://settings-search-restore?cat=search",
                    "btn danger", confirm="Restore the default search engine list? Custom engines will be removed.")
    return html


def _add_engine_form():
    return """
    <div class="engine-form">
        <div class="form-grid">
            <div><label class="f-label">Name</label>
                <input type="text" class="ctl-input" id="se-name" placeholder="My Search"></div>
            <div><label class="f-label">Keyword</label>
                <input type="text" class="ctl-input" id="se-keyword" placeholder="ms"></div>
            <div class="span2"><label class="f-label">Search URL (use {searchTerms})</label>
                <input type="text" class="ctl-input" id="se-url" placeholder="https://example.com/search?q={searchTerms}"></div>
            <div class="span2"><label class="f-label">Suggestions URL (optional)</label>
                <input type="text" class="ctl-input" id="se-suggest" placeholder="https://example.com/suggest?q={searchTerms}"></div>
        </div>
        <div class="form-actions">
            <button type="button" class="btn primary" data-add-engine>Add search engine</button>
        </div>
    </div>
    """


def _privacy(payload):
    s = payload["settings"]
    cat = "privacy"
    html = ""
    html += _section_title("Browsing data", "Clear locally stored data from Rhodium.")
    html += _button("Clear browsing history", "rhodium://settings-clear-data?cat=privacy&what=history",
                    "btn", confirm="Clear your browsing history?")
    html += _button("Clear cookies and site data", "rhodium://settings-cookie-clear?cat=privacy",
                    "btn", confirm="Clear all cookies and site data?")
    html += _button("Clear cached images and files", "rhodium://settings-clear-data?cat=privacy&what=cache",
                    "btn", confirm="Clear the browsing cache?")
    html += _button("Clear download history", "rhodium://settings-downloads-clear?cat=privacy",
                    "btn", confirm="Clear download history?")
    html += _button("Clear all browsing data", "rhodium://settings-clear-data?cat=privacy&what=all",
                    "btn danger", confirm="Clear history, cookies, cache, site storage and download history?")
    html += "<div class='sec-divider'></div>"
    html += _section_title("Privacy preferences", "Preferences about how sites track you.")
    html += _toggle("privacy.do_not_track", "Send a 'Do Not Track' request",
                    s.get("privacy.do_not_track", False), cat,
                    desc="Asked to websites via the DNT header. Many sites ignore it.")
    html += _toggle("privacy.tracking_protection", "Tracking protection",
                    s.get("privacy.tracking_protection", True), cat,
                    desc="Blocks known trackers where Rhodium's protection is active.")
    html += _toggle("privacy.safe_browsing", "Safe browsing",
                    s.get("privacy.safe_browsing", False), cat,
                    desc="Warns about dangerous sites. QtWebEngine does not ship a protection provider — this is a preference only.")
    html += "<div class='sec-divider'></div>"
    html += _section_title("Website features", "Controls for page features.")
    html += _toggle("privacy.javascript_enabled", "JavaScript",
                    s.get("privacy.javascript_enabled", True), cat)
    html += _toggle("privacy.local_storage_enabled", "Local storage",
                    s.get("privacy.local_storage_enabled", True), cat)
    html += _toggle("privacy.cookies_enabled", "Accept cookies",
                    s.get("privacy.cookies_enabled", True), cat)
    html += _toggle("privacy.cache_enabled", "Cache (disk)",
                    s.get("privacy.cache_enabled", True), cat)
    html += _toggle("privacy.popups_blocked", "Block pop-up windows",
                    s.get("privacy.popups_blocked", True), cat)
    html += _select("privacy.notifications", "Notifications",
                    [("allow", "Allow"), ("ask", "Ask"), ("block", "Block")],
                    s.get("privacy.notifications", "ask"), cat)
    html += _select("privacy.location", "Location",
                    [("allow", "Allow"), ("ask", "Ask"), ("block", "Block")],
                    s.get("privacy.location", "ask"), cat)
    html += _select("privacy.camera", "Camera",
                    [("allow", "Allow"), ("ask", "Ask"), ("block", "Block")],
                    s.get("privacy.camera", "ask"), cat)
    html += _select("privacy.microphone", "Microphone",
                    [("allow", "Allow"), ("ask", "Ask"), ("block", "Block")],
                    s.get("privacy.microphone", "ask"), cat)
    html += f"""
    <div class="note">
        <strong>Note:</strong> some preferences describe Rhodium's intent but cannot be enforced
        directly by QtWebEngine without an integrated protection provider. They are stored
        centrally and exposed here for transparency.
    </div>
    """
    return html


def _cookies(payload):
    cookies = payload.get("cookies", [])
    cat = "cookies"
    html = ""
    html += _section_title("Cookies", "Cookies stored by the shared QWebEngineProfile.")
    html += f"""
    <div class="toolbar">
        <input type="search" class="search" id="cookie-search" placeholder="Search cookies by domain or name…">
        <button type="button" class="btn danger" data-route="rhodium://settings-cookie-clear?cat=cookies" data-confirm="Delete all cookies?">Clear all</button>
    </div>
    <div class="cookie-table-wrap"><table class="cookie-table" id="cookie-table">
        <thead><tr><th>Domain</th><th>Name</th><th>Value</th><th>Expires</th><th>Secure</th><th></th></tr></thead>
        <tbody id="cookie-body">
    """
    if not cookies:
        html += '<tr><td colspan="6" class="empty-td">No cookies found</td></tr>'
    for c in cookies:
        domain = _es(c.get("domain", ""))
        name = _es(c.get("name", ""))
        value = _es(c.get("value", ""))
        if len(value) > 24:
            value = value[:24] + "…"
        secure = "Yes" if c.get("secure") else "No"
        exp = _es(c.get("expiration") or ("Session" if c.get("is_session") else "Expired"))
        del_url = f"rhodium://settings-cookie-delete?cat=cookies&domain={_q(c.get('domain',''))}&name={_q(c.get('name',''))}"
        html += f"""
        <tr class="cookie-row" data-domain="{_q(c.get('domain',''))}" data-name="{_q(c.get('name',''))}">
            <td class="c-domain">{domain}</td>
            <td>{name}</td>
            <td class="c-value" title="{value}">{value}</td>
            <td>{exp}</td>
            <td>{secure}</td>
            <td>
                <button type="button" class="btn mini danger" data-route="rhodium://settings-cookie-delete-domain?cat=cookies&domain={_q(c.get('domain',''))}" data-confirm="Delete all cookies for this domain?">Clear domain</button>
                <button type="button" class="btn mini danger" data-route="{del_url}" data-confirm="Delete this cookie?">Delete</button>
            </td>
        </tr>
        """
    html += "</tbody></table></div>"
    return html


def _downloads(payload):
    s = payload["settings"]
    cat = "downloads"
    n = payload.get("downloads_count", 0)
    html = ""
    html += _section_title("Downloads", "Where files are saved and how downloads behave.")
    html += _text("downloads.directory", "Download location", s.get("downloads.directory", ""),
                  cat, placeholder="C:\\Users\\You\\Downloads")
    html += _button("Browse…", "rhodium://settings-downloads-browse?cat=downloads", "btn")
    html += _toggle("downloads.ask_where", "Ask where to save each file",
                    s.get("downloads.ask_where", False), cat)
    html += _toggle("downloads.open_downloads_page", "Open the downloads page when a download starts",
                    s.get("downloads.open_downloads_page", False), cat)
    html += _toggle("downloads.notify_completion", "Show a notification when a download finishes",
                    s.get("downloads.notify_completion", True), cat)
    html += "<div class='sec-divider'></div>"
    html += _section_title("Download activity", f"{n} downloads in the current session.")
    html += _button("Open downloads folder", "rhodium://settings-downloads-open-folder?cat=downloads", "btn")
    html += _button("Open downloads page", "rhodium://downloads?cat=downloads", "btn")
    html += _button("Clear download history", "rhodium://settings-downloads-clear?cat=downloads",
                    "btn danger", confirm="Clear download history?")
    return html


def _bookmarks(payload):
    cat = "bookmarks"
    count = payload.get("bookmarks_count", 0)
    html = ""
    html += _section_title("Bookmarks", f"You have {count} saved bookmark{'s' if count != 1 else ''}.")
    html += _button("Manage bookmarks", "rhodium://settings-bookmarks-open?cat=bookmarks", "btn")
    html += _button("Open bookmarks page", "rhodium://bookmarks?cat=bookmarks", "btn")
    html += "<div class='sec-divider'></div>"
    html += _section_title("Bring your bookmarks", "Import and export in a portable format.")
    html += _button("Import bookmarks…", "rhodium://settings-bookmarks-import?cat=bookmarks", "btn")
    html += _button("Export bookmarks…", "rhodium://settings-bookmarks-export?cat=bookmarks", "btn")
    html += """
    <div class="note">Bookmarks are stored in a single shared JSON backend
        (in your Rhodium profile). The Settings page manages that same data —
        there is no duplicate database.</div>
    """
    return html


def _history(payload):
    cat = "history"
    count = payload.get("history_count", 0)
    html = ""
    html += _section_title("Browsing history", f"{count} visits recorded in your history.")
    html += _button("View full history", "rhodium://settings-history-open?cat=history", "btn")
    html += "<div class='sec-divider'></div>"
    html += _section_title("Clear history", "Remove history from a selected time period.")
    html += _button("Last hour", "rhodium://settings-history-clear?cat=history&range=hour", "btn", confirm="Clear the last hour of history?")
    html += _button("Today", "rhodium://settings-history-clear?cat=history&range=today", "btn", confirm="Clear today's history?")
    html += _button("Today and yesterday", "rhodium://settings-history-clear?cat=history&range=yesterday", "btn", confirm="Clear today's and yesterday's history?")
    html += _button("All history", "rhodium://settings-history-clear?cat=history&range=all",
                    "btn danger", confirm="Clear all history?")
    return html


def _appearance(payload):
    s = payload["settings"]
    cat = "appearance"
    html = ""
    html += _section_title("Theme", "Choose how Rhodium looks.")
    html += _radio("general.theme", "Theme", "theme",
                   [("light", "Light"), ("dark", "Dark"), ("system", "System")],
                   s.get("general.theme", "light"), cat)
    html += _text("appearance.accent_color", "Accent colour", s.get("appearance.accent_color", "#6D4FD8"),
                  cat, placeholder="#6D4FD8")
    html += "<div class='sec-divider'></div>"
    html += _section_title("Toolbar & tabs", "Customize the browser chrome.")
    html += _toggle("appearance.show_home_button", "Show the Home button",
                    s.get("appearance.show_home_button", True), cat)
    html += _toggle("appearance.show_bookmarks_bar", "Show the bookmarks bar",
                    s.get("appearance.show_bookmarks_bar", False), cat)
    html += _select("appearance.toolbar_style", "Toolbar style",
                    [("default", "Default"), ("compact", "Compact")],
                    s.get("appearance.toolbar_style", "default"), cat)
    html += "<div class='sec-divider'></div>"
    html += _section_title("Content display", "Text size and zoom.")
    html += _radio("general.font_size", "Font size", "font",
                   [("small", "Small"), ("medium", "Medium"), ("large", "Large")],
                   s.get("general.font_size", "medium"), cat)
    html += _text("general.zoom", "Default zoom (%)", s.get("general.zoom", 100), cat, placeholder="100")
    html += _select("appearance.home_background", "Homepage background",
                    [("gradient", "Soft gradient"), ("flat", "Flat"), ("image", "Wallpaper")],
                    s.get("appearance.home_background", "gradient"), cat)
    return html


def _tabs(payload):
    s = payload["settings"]
    cat = "tabs"
    html = ""
    html += _section_title("Session", "What to restore when Rhodium starts.")
    html += _toggle("tabs.restore_session", "Restore the previous session",
                    s.get("tabs.restore_session", False), cat,
                    desc="Reopen all tabs from your last session on startup.")
    html += "<div class='sec-divider'></div>"
    html += _section_title("Tab behaviour", "How tabs open and close.")
    html += _toggle("tabs.open_background", "Open new tabs in the background",
                    s.get("tabs.open_background", False), cat)
    html += _toggle("tabs.confirm_close_multiple", "Ask before closing multiple tabs",
                    s.get("tabs.confirm_close_multiple", True), cat)
    html += _toggle("tabs.close_button_on_active", "Show close button on active tab",
                    s.get("tabs.close_button_on_active", True), cat)
    return html


def _permissions(payload):
    s = payload["settings"]
    cat = "permissions"
    html = ""
    html += _section_title("Site permissions", "Default permissions requested by websites.")
    html += _select("privacy.camera", "Camera",
                    [("allow", "Allow"), ("ask", "Ask"), ("block", "Block")],
                    s.get("privacy.camera", "ask"), cat)
    html += _select("privacy.microphone", "Microphone",
                    [("allow", "Allow"), ("ask", "Ask"), ("block", "Block")],
                    s.get("privacy.microphone", "ask"), cat)
    html += _select("privacy.location", "Location",
                    [("allow", "Allow"), ("ask", "Ask"), ("block", "Block")],
                    s.get("privacy.location", "ask"), cat)
    html += _select("privacy.notifications", "Notifications",
                    [("allow", "Allow"), ("ask", "Ask"), ("block", "Block")],
                    s.get("privacy.notifications", "ask"), cat)
    html += _toggle("privacy.javascript_enabled", "JavaScript",
                    s.get("privacy.javascript_enabled", True), cat)
    html += _toggle("privacy.popups_blocked", "Block pop-up windows",
                    s.get("privacy.popups_blocked", True), cat)
    html += _toggle("privacy.local_storage_enabled", "Clipboard access",
                    s.get("privacy.local_storage_enabled", True), cat,
                    desc="Allow pages to read the clipboard. QtWebEngine may still prompt per-site.")
    html += f"""
    <div class="note">These defaults are applied at the shared profile level. QtWebEngine
        enforces the enforcement ones natively; the rest are stored centrally as preferences.
        Per-site overrides are not yet exposed in this UI.</div>
    """
    return html


def _passwords(payload):
    html = """
    <div class="empty-state">
        <div class="empty-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6"
                 stroke-linecap="round" stroke-linejoin="round">
                <rect x="4" y="10" width="16" height="11" rx="2"/>
                <path d="M8 10V7a4 4 0 0 1 8 0v3"/>
                <circle cx="12" cy="15.5" r="1.4"/>
            </svg>
        </div>
        <div class="empty-title">Password Manager</div>
        <div class="empty-desc">Save and autofill passwords for your favourite sites — right here.</div>
        <div class="empty-badge">Coming soon</div>
        <div class="empty-sub">Password management is not available yet. This section will be
            completed in a future release. No passwords are stored or captured.</div>
    </div>
    """
    return html


_RENDERERS = {
    "general": _general,
    "search": _search_engine,
    "privacy": _privacy,
    "cookies": _cookies,
    "downloads": _downloads,
    "bookmarks": _bookmarks,
    "history": _history,
    "appearance": _appearance,
    "tabs": _tabs,
    "permissions": _permissions,
    "passwords": _passwords,
}


def get_settings_page_html(payload) -> str:
    cat = payload.get("cat", "general")
    if cat not in _RENDERERS:
        cat = "general"
    theme = payload.get("theme", "light")
    content_html = _RENDERERS[cat](payload)

    nav_items = ""
    for cid, label, _sub in _CATEGORIES:
        active = ' active' if cid == cat else ''
        nav_items += f'<button type="button" class="nav-item{active}" data-cat="{cid}">{_es(label)}</button>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Settings — Rhodium</title>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
{css_vars(theme=theme)}
html, body {{ width: 100%; height: 100%; }}
body {{
    background: var(--bg_app); color: var(--text_primary);
    font-family: "Segoe UI", Inter, -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 13px; overflow: hidden;
}}
.layout {{ display: flex; height: 100vh; }}

/* ── Sidebar ─────────────────────────────────────────────── */
.sidebar {{
    width: 240px; flex-shrink: 0; border-right: 1px solid var(--border);
    display: flex; flex-direction: column; background: var(--bg_surface);
}}
.side-head {{
    padding: 18px 18px 12px; display: flex; align-items: center; gap: 10px;
}}
.side-logo {{
    width: 30px; height: 30px; border-radius: 9px; display: grid; place-items: center;
    background: linear-gradient(135deg, var(--accent), #8B6FE0);
}}
.side-logo svg {{ width: 16px; height: 16px; stroke: #fff; }}
.side-title {{ font-size: 15px; font-weight: 700; letter-spacing: -.01em; }}
.side-search {{ padding: 0 12px 10px; }}
.side-search input {{
    width: 100%; padding: 8px 12px; border-radius: 9px; font-size: 12px;
    background: var(--bg_sunken); border: 1px solid transparent; color: var(--text_primary);
    outline: none; transition: border-color .15s;
}}
.side-search input:focus {{ border-color: var(--accent); background: var(--bg_surface); }}
.nav {{ flex: 1; overflow-y: auto; padding: 4px 10px 12px; display: flex; flex-direction: column; gap: 2px; }}
.nav-item {{
    text-align: left; padding: 9px 12px; border: none; border-radius: 9px;
    background: transparent; color: var(--text_secondary); font-size: 13px;
    cursor: pointer; transition: background .15s, color .15s;
}}
.nav-item:hover {{ background: var(--bg_hover); color: var(--text_primary); }}
.nav-item.active {{ background: var(--accent_soft); color: var(--accent); font-weight: 600; }}
.nav-item.hidden {{ display: none; }}
.side-foot {{ padding: 12px 18px; border-top: 1px solid var(--border); font-size: 11px; color: var(--text_muted); }}

/* ── Content ─────────────────────────────────────────────── */
.content {{ flex: 1; overflow-y: auto; }}
.content-inner {{ max-width: 780px; margin: 0 auto; padding: 28px 32px 56px; }}

/* ── Sections & controls ─────────────────────────────────── */
.sec-head {{ margin-bottom: 14px; }}
.sec-title {{ font-size: 22px; font-weight: 700; letter-spacing: -.02em; }}
.sec-sub {{ font-size: 12.5px; color: var(--text_muted); margin-top: 3px; }}
.sec-divider {{ height: 1px; background: var(--border); margin: 22px 0; }}
.ctl-row {{
    display: flex; align-items: center; justify-content: space-between; gap: 16px;
    padding: 12px 2px; border-bottom: 1px solid var(--border);
}}
.ctl-row.col {{ flex-direction: column; align-items: stretch; }}
.ctl-info {{ min-width: 0; }}
.ctl-label {{ font-size: 13px; font-weight: 600; }}
.ctl-desc {{ font-size: 11.5px; color: var(--text_secondary); margin-top: 2px; line-height: 1.45; }}
.ctl-select, .ctl-input {{
    background: var(--bg_sunken); border: 1px solid transparent; border-radius: 9px;
    color: var(--text_primary); padding: 8px 12px; font-size: 12.5px; outline: none;
    transition: border-color .15s, background .15s; min-width: 170px;
}}
.ctl-input {{ min-width: 260px; text-align: right; }}
.ctl-select:focus, .ctl-input:focus {{ border-color: var(--accent); background: var(--bg_surface); }}

/* Toggle switch */
.switch {{ position: relative; display: inline-block; width: 42px; height: 24px; flex-shrink: 0; }}
.switch input {{ opacity: 0; width: 0; height: 0; }}
.slider {{
    position: absolute; inset: 0; border-radius: 999px; background: var(--bg_active);
    transition: background .18s; cursor: pointer;
}}
.slider:before {{
    content: ""; position: absolute; width: 18px; height: 18px; left: 3px; top: 3px;
    border-radius: 50%; background: var(--bg_surface); box-shadow: var(--shadow_sm);
    transition: transform .18s;
}}
.switch input:checked + .slider {{ background: var(--accent); }}
.switch input:checked + .slider:before {{ transform: translateX(18px); }}
.switch input:disabled + .slider {{ opacity: .4; cursor: not-allowed; }}

/* Radio */
.radio-group {{ display: flex; flex-direction: column; gap: 8px; }}
.radio {{ display: inline-flex; align-items: center; gap: 9px; cursor: pointer; font-size: 13px; }}
.radio input {{ display: none; }}
.radio-mark {{
    width: 18px; height: 18px; border-radius: 50%; border: 2px solid var(--border_strong);
    display: inline-block; position: relative; transition: border-color .15s;
}}
.radio input:checked + .radio-mark {{ border-color: var(--accent); }}
.radio input:checked + .radio-mark:after {{
    content: ""; position: absolute; inset: 3px; border-radius: 50%; background: var(--accent);
}}
.radio-mark-static {{
    width: 16px; height: 16px; border-radius: 50%; border: 2px solid var(--border_strong);
    display: inline-block; opacity: 0; position: absolute;
}}
.engine-radio input:checked ~ .radio-mark-static {{ opacity: 1; border-color: var(--accent); }}
.engine-radio input:checked ~ .radio-mark-static:after {{
    content: ""; position: absolute; inset: 3px; border-radius: 50%; background: var(--accent);
}}

/* Buttons */
.btn {{
    background: var(--bg_sunken); color: var(--text_secondary); border: 1px solid transparent;
    border-radius: 9px; padding: 8px 14px; font-size: 12.5px; cursor: pointer;
    display: inline-flex; align-items: center; gap: 6px; margin: 4px 6px 4px 0;
    transition: background .15s, color .15s, border-color .15s;
}}
.btn:hover {{ background: var(--bg_hover); color: var(--text_primary); border-color: var(--border_strong); }}
.btn.primary {{ background: var(--accent); color: var(--on_accent); font-weight: 600; }}
.btn.primary:hover {{ background: var(--accent_hover); color: var(--on_accent); }}
.btn.danger {{ background: var(--danger_soft); color: var(--danger); }}
.btn.danger:hover {{ background: var(--danger); color: var(--on_accent); border-color: transparent; }}
.btn.mini {{ padding: 5px 10px; font-size: 11px; border-radius: 7px; }}

/* Note */
.note {{
    margin-top: 16px; padding: 12px 14px; border-radius: 10px; font-size: 12px;
    line-height: 1.5; color: var(--text_secondary); background: var(--bg_sunken);
    border: 1px solid var(--border);
}}
.note strong {{ color: var(--text_primary); }}

/* Search engine list */
.engine-list {{ display: flex; flex-direction: column; gap: 8px; }}
.engine-row {{
    position: relative; display: flex; align-items: center; gap: 12px;
    padding: 10px 14px; border-radius: 12px; background: var(--bg_surface);
    border: 1px solid var(--border); transition: border-color .15s, box-shadow .15s;
}}
.engine-row:hover {{ border-color: var(--border_strong); box-shadow: var(--shadow_sm); }}
.engine-row:has(input:checked) {{ border-color: var(--accent); box-shadow: 0 0 0 2px var(--accent_soft); }}
.engine-radio {{ position: relative; display: inline-flex; }}
.engine-info {{ flex: 1; min-width: 0; }}
.engine-name {{ font-size: 13px; font-weight: 600; }}
.engine-name .kw {{ color: var(--accent); font-weight: 700; margin-left: 6px; font-size: 11px; }}
.engine-url {{ font-size: 11px; color: var(--text_muted); margin-top: 2px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
.engine-actions {{ display: flex; gap: 6px; }}

/* Add engine form */
.engine-form {{
    background: var(--bg_surface); border: 1px solid var(--border); border-radius: 14px;
    padding: 16px; margin-top: 8px;
}}
.form-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
.span2 {{ grid-column: span 2; }}
.f-label {{ display: block; font-size: 11px; color: var(--text_muted); margin-bottom: 5px; font-weight: 600; }}
.form-grid .ctl-input {{ width: 100%; text-align: left; min-width: 0; }}
.form-actions {{ margin-top: 14px; }}

/* Cookies table */
.toolbar {{ display: flex; gap: 10px; align-items: center; margin: 14px 0 12px; flex-wrap: wrap; }}
.search {{
    background: var(--bg_sunken); border: 1px solid transparent; border-radius: 9px;
    color: var(--text_primary); padding: 8px 13px; font-size: 12.5px; width: min(320px, 100%);
    outline: none; transition: border-color .15s;
}}
.search:focus {{ border-color: var(--accent); background: var(--bg_surface); }}
.cookie-table-wrap {{ border: 1px solid var(--border); border-radius: 12px; overflow: auto; background: var(--bg_surface); }}
.cookie-table {{ width: 100%; border-collapse: collapse; min-width: 680px; }}
.cookie-table th {{
    text-align: left; font-size: 10px; letter-spacing: .08em; text-transform: uppercase;
    color: var(--text_muted); background: var(--bg_inset); padding: 10px 12px;
    border-bottom: 1px solid var(--border); position: sticky; top: 0;
}}
.cookie-table td {{ padding: 10px 12px; border-bottom: 1px solid var(--border); font-size: 12px;
    word-break: break-all; vertical-align: middle; }}
.cookie-table tr:last-child td {{ border-bottom: none; }}
.cookie-table tr:hover {{ background: var(--bg_hover); }}
.c-domain {{ font-weight: 600; color: var(--accent); }}
.c-value {{ max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--text_muted); }}
.empty-td {{ text-align: center; color: var(--text_muted); padding: 28px !important; }}

/* Empty state (password manager) */
.empty-state {{
    text-align: center; padding: 48px 24px; display: flex; flex-direction: column;
    align-items: center; gap: 12px;
}}
.empty-icon {{
    width: 72px; height: 72px; border-radius: 20px; display: grid; place-items: center;
    background: var(--accent_soft); color: var(--accent);
}}
.empty-icon svg {{ width: 34px; height: 34px; }}
.empty-title {{ font-size: 20px; font-weight: 700; }}
.empty-desc {{ font-size: 13px; color: var(--text_secondary); max-width: 360px; }}
.empty-badge {{
    font-size: 11px; font-weight: 700; letter-spacing: .08em; text-transform: uppercase;
    padding: 6px 14px; border-radius: 999px; background: var(--accent_soft);
    color: var(--accent); border: 1px solid var(--accent_soft_hover);
}}
.empty-sub {{ font-size: 12px; color: var(--text_muted); max-width: 400px; line-height: 1.5; }}

@media (max-width: 720px) {{
    .sidebar {{ width: 180px; }}
    .content-inner {{ padding: 20px 18px 40px; }}
    .ctl-input {{ min-width: 160px; }}
}}
</style>
</head>
<body>
<div class="layout">
    <aside class="sidebar">
        <div class="side-head">
            <div class="side-logo">
                <svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="8.5"/><path d="M3.8 12h16.4"/>
                    <path d="M12 3.5c2.4 2.3 3.6 5.1 3.6 8.5S14.4 18.2 12 20.5"/>
                    <path d="M12 3.5C9.6 5.8 8.4 8.6 8.4 12s1.2 6.2 3.6 8.5"/>
                </svg>
            </div>
            <div class="side-title">Settings</div>
        </div>
        <div class="side-search">
            <input type="search" id="filter" placeholder="Search settings…">
        </div>
        <nav class="nav" id="nav">
            {nav_items}
        </nav>
        <div class="side-foot" id="result-count"></div>
    </aside>
    <main class="content">
        <div class="content-inner">
            {content_html}
        </div>
    </main>
</div>
<script>
const CAT = {json.dumps(cat)};
const NAV = document.querySelectorAll('.nav-item');
const countEl = document.getElementById('result-count');

function navTo(cat) {{
    window.location.href = 'rhodium://settings?cat=' + encodeURIComponent(cat);
}}

NAV.forEach(btn => {{
    btn.addEventListener('click', () => navTo(btn.dataset.cat));
}});

// Sidebar filter
const filterEl = document.getElementById('filter');
function applyFilter() {{
    const q = filterEl.value.trim().toLowerCase();
    let shown = 0;
    NAV.forEach(btn => {{
        const match = !q || btn.textContent.toLowerCase().includes(q);
        btn.classList.toggle('hidden', !match);
        if (match) shown++;
    }});
    countEl.textContent = q ? shown + ' categories match' : '';
}}
filterEl.addEventListener('input', applyFilter);

// Generic single-key setter (select, radio, toggle, text commit)
function applySet(el) {{
    const key = el.dataset.set;
    const cat = el.dataset.cat || CAT;
    let value;
    if (el.type === 'checkbox') {{
        value = el.checked ? 'true' : 'false';
    }} else {{
        value = el.value;
    }}
    window.location.href = 'rhodium://settings-set?cat=' + encodeURIComponent(cat)
        + '&key=' + encodeURIComponent(key) + '&value=' + encodeURIComponent(value);
}}

document.querySelectorAll('[data-set]').forEach(el => {{
    if (el.type === 'checkbox') {{
        el.addEventListener('change', () => applySet(el));
    }} else if (el.tagName === 'SELECT') {{
        el.addEventListener('change', () => applySet(el));
    }} else if (el.type === 'radio') {{
        el.addEventListener('change', () => applySet(el));
    }} else if (el.tagName === 'INPUT' && el.type === 'text') {{
        el.addEventListener('blur', () => {{
            if (document.activeElement !== el) applySet(el);
        }});
        el.addEventListener('keydown', e => {{
            if (e.key === 'Enter') {{
                e.preventDefault();
                applySet(el);
            }}
        }});
    }}
}});

// Buttons with data-route
document.querySelectorAll('[data-route]').forEach(btn => {{
    btn.addEventListener('click', () => {{
        const confirmMsg = btn.dataset.confirm;
        if (confirmMsg && !window.confirm(confirmMsg)) return;
        window.location.href = btn.dataset.route;
    }});
}});

// Add search engine
const addBtn = document.querySelector('[data-add-engine]');
if (addBtn) {{
    addBtn.addEventListener('click', () => {{
        const name = document.getElementById('se-name').value.trim();
        const url = document.getElementById('se-url').value.trim();
        const suggest = document.getElementById('se-suggest').value.trim();
        const keyword = document.getElementById('se-keyword').value.trim();
        if (!name || !url) {{
            alert('Name and search URL are required.');
            return;
        }}
        if (!url.includes('{{searchTerms}}')) {{
            alert('The search URL must contain {{searchTerms}}.');
            return;
        }}
        window.location.href = 'rhodium://settings-search-add?cat=search'
            + '&name=' + encodeURIComponent(name)
            + '&url=' + encodeURIComponent(url)
            + '&suggest=' + encodeURIComponent(suggest)
            + '&keyword=' + encodeURIComponent(keyword);
    }});
}}

// Cookie table local search
const cookieSearch = document.getElementById('cookie-search');
if (cookieSearch) {{
    cookieSearch.addEventListener('input', () => {{
        const q = cookieSearch.value.toLowerCase();
        document.querySelectorAll('.cookie-row').forEach(row => {{
            const matches = (row.dataset.domain + ' ' + row.dataset.name).toLowerCase().includes(q);
            row.style.display = matches ? '' : 'none';
        }});
    }});
}}
</script>
</body>
</html>"""
