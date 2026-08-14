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

def get_home_page_html() -> str:
    return """<!DOCTYPE html>
        <html lang="en">
        <head>
        <meta charset="UTF-8">
        <title>Rhodium</title>

        <style>

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        html,
        body {
            width: 100%;
            height: 100%;
        }

        body {
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
        }

        /* =========================================================
        MAIN
        ========================================================= */

        .container {
            width: 680px;
            max-width: calc(100vw - 60px);

            display: flex;
            flex-direction: column;
            align-items: center;

            transform: translateY(-28px);
        }

        /* =========================================================
        BRAND
        ========================================================= */

        .brand {
            display: flex;
            align-items: center;
            gap: 11px;

            margin-bottom: 34px;

            color: #e9ebef;

            font-size: 25px;
            font-weight: 600;
            letter-spacing: -0.7px;
        }

        .brand-mark {
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
        }

        .brand-mark svg {
            width: 21px;
            height: 21px;

            stroke: #9cb7d8;
        }

        /* =========================================================
        SEARCH
        ========================================================= */

        .search {
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
        }

        .search:hover {
            background: #171a1f;
            border-color: #363b44;
        }

        .search:focus-within {
            background: #171a1f;
            border-color: #466b9f;

            box-shadow:
                0 0 0 3px rgba(70,107,159,.10);
        }

        .search-icon {
            width: 20px;
            height: 20px;

            margin-left: 17px;
            margin-right: 12px;

            color: #777e89;
        }

        .search input {
            width: 100%;
            height: 100%;

            background: transparent;
            border: none;
            outline: none;

            color: #e9ebef;

            font-size: 14px;
        }

        .search input::placeholder {
            color: #777d87;
        }

        /* =========================================================
        SHORTCUTS
        ========================================================= */

        .shortcuts {
            width: 100%;

            display: flex;
            justify-content: center;

            gap: 8px;

            margin-top: 28px;
        }

        .shortcut {
            width: 76px;

            display: flex;
            flex-direction: column;
            align-items: center;

            gap: 8px;

            color: #777d87;

            font-size: 11px;

            text-decoration: none;

            cursor: pointer;
        }

        .shortcut-button {
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
        }

        .shortcut-button svg {
            width: 18px;
            height: 18px;

            stroke: #8e96a1;
        }

        .shortcut:hover {
            color: #cdd1d7;
        }

        .shortcut:hover .shortcut-button {
            background: #1b1e23;
            border-color: #3a4049;

            transform: translateY(-2px);
        }

        .shortcut:hover svg {
            stroke: #c5ccd5;
        }

        /* ADD BUTTON */

        .shortcut.add .shortcut-button {
            border-style: dashed;
        }

        .shortcut.add svg {
            stroke: #666d77;
        }

        /* =========================================================
        FOOTER
        ========================================================= */

        .footer {
            margin-top: 34px;

            color: #4f555e;

            font-size: 10px;
            letter-spacing: .2px;
        }

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
            .addEventListener('keydown', e => {

                if (e.key === 'Enter') {

                    const value = e.target.value.trim();

                    if (value) {
                        nav(value);
                    }

                }

            });


        function nav(query) {

            window.location.href =
                'rhodium://navigate?q=' +
                encodeURIComponent(query);

        }


        function addLink() {

            const name = prompt('Link name:');
            const url = prompt('URL:');

            if (url) {
                nav(url);
            }

        }

        </script>

        </body>
        </html>"""
