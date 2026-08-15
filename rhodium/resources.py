import urllib.parse
import os

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
        }

        QTabWidget#BrowserTabs::tab-bar {
            alignment: left;
        }


        /* TAB BAR */

        QTabBar {
            background: #111318;

            qproperty-drawBase: 0;

            border: none;

            min-height: 38px;
            max-height: 38px;
        }


        /* INDIVIDUAL TAB */

        QTabBar::tab {
            background: #111318;

            color: #858c97;

            border: none;
            border-top-left-radius: 9px;
            border-top-right-radius: 9px;

            padding: 0px 12px;

            margin-top: 4px;
            margin-right: 2px;

            min-width: 150px;
            max-width: 220px;

            min-height: 34px;
            max-height: 34px;

            font-size: 12px;
        }


        /* HOVERED TAB */

        QTabBar::tab:hover {
            background: #191d23;
            color: #cbd0d8;
        }


        /* ACTIVE TAB */

        QTabBar::tab:selected {
            background: #0b0d10;

            color: #f1f3f6;

            border-top: 1px solid #2d3540;
            border-left: 1px solid #252b33;
            border-right: 1px solid #252b33;

            margin-top: 2px;

            min-height: 36px;
            max-height: 36px;
        }


        /* Active tab bottom accent */

        QTabBar::tab:selected {
            border-bottom: 2px solid #4c78b5;
        }


        /* =========================================================
        TAB CLOSE BUTTON
        ========================================================= */

        QTabBar::close-button {
            image: url(style/icons/close (2).png);

            width: 18px;
            height: 18px;

            subcontrol-position: right;

            margin-left: 1px;
            margin-right: 1px;

            border-radius: 5px;
        }

        QTabBar::close-button:hover {
            background: #2a2f37;
        }

        QTabBar::close-button:pressed {
            background: #353b44;
        }


        /* =========================================================
        NEW TAB BUTTON
        ========================================================= */

        QToolButton#NewTabButton {
            background: transparent;

            border: none;
            border-radius: 8px;

            padding: 6px;

            margin-left: 4px;
            margin-top: 3px;

            color: #8e96a2;
        }

        QToolButton#NewTabButton:hover {
            background: #1d2128;
            color: #e7eaf0;
        }

        QToolButton#NewTabButton:pressed {
            background: #282d35;
        }


        /* =========================================================
        TAB SCROLL BUTTONS
        ========================================================= */

        QTabBar QToolButton {
            background: #15181d;

            border: none;
            border-radius: 6px;

            color: #9da4ae;

            margin: 5px 3px;

            padding: 4px;
        }

        QTabBar QToolButton:hover {
            background: #242930;
            color: #ffffff;
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

def get_home_page_html(shortcuts=None) -> str:
    if shortcuts is None:
        shortcuts = []

    shortcuts_html = ""
    for s in shortcuts:
        name = s.get("name", "Shortcut")
        url = s.get("url", "#")
        fav_path = s.get("favicon", "")
        
        icon_element = ""
        if fav_path and os.path.exists(fav_path):
            img_url = "file:///" + fav_path.replace("\\", "/")
            icon_element = f'<img src="{img_url}" style="width: 22px; height: 22px; border-radius: 4px; object-fit: contain;" />'
        else:
            icon_element = """
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" style="width: 22px; height: 22px;">
                            <circle cx="12" cy="12" r="10"/>
                            <line x1="2" y1="12" x2="22" y2="12"/>
                            <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/>
                        </svg>
            """
            
        shortcuts_html += f"""
                <div class="shortcut-wrapper" style="position: relative; display: inline-block;">
                    <div class="shortcut" onclick="nav('{url}')">
                        <div class="shortcut-button">
                            {icon_element}
                        </div>
                        <span>{name}</span>
                    </div>
                    <div class="shortcut-actions" style="position: absolute; top: -5px; right: 0px; display: none; gap: 4px; background: #1f232a; border-radius: 6px; border: 1px solid #333333; padding: 2px; z-index: 10;">
                        <span class="action-btn" onclick="event.stopPropagation(); window.location.href='rhodium://edit-shortcut?url={urllib.parse.quote(url)}'" style="cursor: pointer; padding: 2px 4px; font-size: 11px; color: #aaa;">✏️</span>
                        <span class="action-btn" onclick="event.stopPropagation(); window.location.href='rhodium://delete-shortcut?url={urllib.parse.quote(url)}'" style="cursor: pointer; padding: 2px 4px; font-size: 11px; color: #f44;">×</span>
                    </div>
                </div>
        """

    shortcuts_html += """
                <div class="shortcut add" onclick="window.location.href='rhodium://add-shortcut'">
                    <div class="shortcut-button">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" style="width: 22px; height: 22px;">
                            <path d="M12 5v14"/>
                            <path d="M5 12h14"/>
                        </svg>
                    </div>
                    <span>Add</span>
                </div>
    """

    return f"""<!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="UTF-8">
        <title>Rhodium</title>

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

        .container {{
            width: 680px;
            max-width: calc(100vw - 60px);

            display: flex;
            flex-direction: column;
            align-items: center;

            transform: translateY(-28px);
        }}

        /* =========================================================
        BRAND
        ========================================================= */

        .brand {{
            display: flex;
            align-items: center;
            gap: 11px;

            margin-bottom: 34px;

            color: #e9ebef;

            font-size: 25px;
            font-weight: 600;
            letter-spacing: -0.7px;
        }}

        .brand-mark {{
            width: 38px;
            height: 38px;

            display: flex;
            align-items: center;
            justify-content: center;

            border-radius: 10px;

            background: linear-gradient(
                145deg,
                #26384f,
                #172131
            );

            border: 1px solid #35485f;

            box-shadow:
                0 8px 25px rgba(0,0,0,.25);
        }}

        .brand-mark svg {{
            width: 21px;
            height: 21px;

            stroke: #9cb7d8;
        }}

        /* =========================================================
        SEARCH
        ========================================================= */

        .search {{
            width: 100%;
            height: 50px;

            display: flex;
            align-items: center;

            background: #15171b;

            border: 1px solid #2b2f36;
            border-radius: 10px;

            transition:
                border-color .18s ease,
                background .18s ease,
                box-shadow .18s ease;
        }}

        .search:hover {{
            background: #171a1f;
            border-color: #363b44;
        }}

        .search:focus-within {{
            background: #171a1f;
            border-color: #466b9f;

            box-shadow:
                0 0 0 3px rgba(70,107,159,.10);
        }}

        .search-icon {{
            width: 20px;
            height: 20px;

            margin-left: 17px;
            margin-right: 12px;

            color: #777e89;
        }}

        .search input {{
            width: 100%;
            height: 100%;

            background: transparent;
            border: none;
            outline: none;

            color: #e9ebef;

            font-size: 14px;
        }}

        .search input::placeholder {{
            color: #777d87;
        }}

        /* =========================================================
        SHORTCUTS
        ========================================================= */

        .shortcuts {{
            width: 100%;

            display: flex;
            justify-content: center;

            gap: 8px;

            margin-top: 28px;
        }}

        .shortcut {{
            width: 76px;

            display: flex;
            flex-direction: column;
            align-items: center;

            gap: 8px;

            color: #777d87;

            font-size: 11px;

            text-decoration: none;

            cursor: pointer;
        }}

        .shortcut-button {{
            width: 42px;
            height: 42px;

            display: flex;
            align-items: center;
            justify-content: center;

            background: #15171b;

            border: 1px solid #282c33;
            border-radius: 9px;

            transition:
                background .15s ease,
                border-color .15s ease,
                transform .15s ease;
        }}

        .shortcut-button svg {{
            width: 18px;
            height: 18px;

            stroke: #8e96a1;
        }}

        .shortcut:hover {{
            color: #cdd1d7;
        }}

        .shortcut:hover .shortcut-button {{
            background: #1b1e23;
            border-color: #3a4049;

            transform: translateY(-2px);
        }}

        .shortcut:hover svg {{
            stroke: #c5ccd5;
        }}

        /* ADD BUTTON */

        .shortcut.add .shortcut-button {{
            border-style: dashed;
        }}

        .shortcut.add svg {{
            stroke: #666d77;
        }}

        /* =========================================================
        FOOTER
        ========================================================= */

        .footer {{
            margin-top: 34px;

            color: #4f555e;

            font-size: 10px;
            letter-spacing: .2px;
        }}

        </style>
        </head>

        <body>

        <div class="container">

            <!-- BRAND -->

            <div class="brand">

                <div class="brand-mark">

                    <svg
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke-width="1.8"
                        stroke-linecap="round"
                        stroke-linejoin="round">

                        <circle cx="12" cy="12" r="8.5"/>
                        <path d="M3.8 12h16.4"/>
                        <path d="M12 3.5c2.4 2.3 3.6 5.1 3.6 8.5S14.4 18.2 12 20.5"/>
                        <path d="M12 3.5C9.6 5.8 8.4 8.6 8.4 12s1.2 6.2 3.6 8.5"/>

                    </svg>

                </div>

                <span>Rhodium</span>

            </div>


            <!-- SEARCH -->

            <div class="search">

                <svg
                    class="search-icon"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="1.8"
                    stroke-linecap="round">

                    <circle cx="11" cy="11" r="6.5"/>
                    <path d="m16 16 4 4"/>

                </svg>

                <input
                    id="q"
                    type="text"
                    placeholder="Search or enter address"
                    autocomplete="off"
                    autofocus
                >

            </div>


            <!-- SHORTCUTS -->

            <div class="shortcuts">

                <!-- Mail -->

                <div
                    class="shortcut"
                    onclick="nav('https://mail.google.com')">

                    <div class="shortcut-button">

                        <svg
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="1.7"
                            stroke-linecap="round"
                            stroke-linejoin="round">

                            <rect x="3" y="5" width="18" height="14" rx="2"/>
                            <path d="m4 7 8 6 8-6"/>

                        </svg>

                    </div>

                    <span>Mail</span>

                </div>


                <!-- Video -->

                <div
                    class="shortcut"
                    onclick="nav('https://youtube.com')">

                    <div class="shortcut-button">

                        <svg
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="1.7"
                            stroke-linecap="round"
                            stroke-linejoin="round">

                            <rect x="3" y="5" width="18" height="14" rx="3"/>
                            <path d="m10 9 5 3-5 3z"/>

                        </svg>

                    </div>

                    <span>Video</span>

                </div>


                <!-- Developer -->

                <div
                    class="shortcut"
                    onclick="nav('https://github.com')">

                    <div class="shortcut-button">

                        <svg
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="1.7"
                            stroke-linecap="round"
                            stroke-linejoin="round">

                            <path d="m8 8-4 4 4 4"/>
                            <path d="m16 8 4 4-4 4"/>
                            <path d="m14 5-4 14"/>

                        </svg>

                    </div>

                    <span>Developer</span>

                </div>


                <!-- News -->

                <div
                    class="shortcut"
                    onclick="nav('https://news.google.com')">

                    <div class="shortcut-button">

                        <svg
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="1.7"
                            stroke-linecap="round"
                            stroke-linejoin="round">

                            <rect x="4" y="4" width="16" height="16" rx="2"/>
                            <path d="M8 8h8"/>
                            <path d="M8 12h8"/>
                            <path d="M8 16h5"/>

                        </svg>

                    </div>

                    <span>News</span>

                </div>


                <!-- Social -->

                <div
                    class="shortcut"
                    onclick="nav('https://twitter.com')">

                    <div class="shortcut-button">

                        <svg
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="1.7"
                            stroke-linecap="round"
                            stroke-linejoin="round">

                            <path d="M5 6h14v9a3 3 0 0 1-3 3H8l-3 3v-15z"/>
                            <path d="M8 10h8"/>
                            <path d="M8 13h5"/>

                        </svg>

                    </div>

                    <span>Social</span>

                </div>


                <!-- Shopping -->

                <div
                    class="shortcut"
                    onclick="nav('https://amazon.com')">

                    <div class="shortcut-button">

                        <svg
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="1.7"
                            stroke-linecap="round"
                            stroke-linejoin="round">

                            <path d="M4 5h2l2 11h10l2-8H7"/>
                            <circle cx="10" cy="20" r="1"/>
                            <circle cx="18" cy="20" r="1"/>

                        </svg>

                    </div>

                    <span>Shopping</span>

                </div>


                <!-- Design -->

                <div
                    class="shortcut"
                    onclick="nav('https://figma.com')">

                    <div class="shortcut-button">

                        <svg
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="1.7"
                            stroke-linecap="round"
                            stroke-linejoin="round">

                            <circle cx="9" cy="6" r="3"/>
                            <circle cx="15" cy="6" r="3"/>
                            <circle cx="9" cy="12" r="3"/>
                            <circle cx="15" cy="12" r="3"/>
                            <path d="M9 15v3a3 3 0 1 0 3-3v-3"/>

                        </svg>

                    </div>

                    <span>Design</span>

                </div>


                <!-- Add -->

                <div
                    class="shortcut add"
                    onclick="addLink()">

                    <div class="shortcut-button">

                        <svg
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            stroke-width="1.7"
                            stroke-linecap="round">

                            <path d="M12 5v14"/>
                            <path d="M5 12h14"/>

                        </svg>

                    </div>

                    <span>Add</span>

                </div>

            </div>


            <div class="footer">
                RHODIUM
            </div>

        </div>


        <script>

        document
            .getElementById('q')
            .addEventListener('keydown', e => {{

                if (e.key === 'Enter') {{

                    const value = e.target.value.trim();

                    if (value) {{
                        nav(value);
                    }}

                }}

            }});


        function nav(query) {{

            window.location.href =
                'rhodium://navigate?q=' +
                encodeURIComponent(query);

        }}


        function addLink() {{

            const name = prompt('Link name:');
            const url = prompt('URL:');

            if (url) {{
                nav(url);
            }}

        }}

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
