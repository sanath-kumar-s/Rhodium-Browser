"""Rhodium design system.

Single source of truth for the light, premium visual language used across the
Qt chrome and every internal `rhodium://` page. Keeping the palette in one
place lets the Qt stylesheet and the inline page CSS stay perfectly in sync.
"""

# ── Palette ───────────────────────────────────────────────────────────────────
PALETTE = {
    # Backgrounds
    "bg_app": "#F5F6F8",          # window / page backdrop
    "bg_surface": "#FFFFFF",      # cards, popups, toolbar, active tab
    "bg_sunken": "#EEEFF3",       # sunken wells / input fills
    "bg_hover": "#F0F1F5",        # hover fill
    "bg_active": "#E8EAF0",       # pressed / selected fill
    "bg_inset": "#FAFAFB",        # subtle inner panel

    # Borders
    "border": "#E8EAF0",
    "border_strong": "#D8DBE4",
    "border_focus": "#B49AE8",

    # Text
    "text_primary": "#1B1D23",
    "text_secondary": "#5B6372",
    "text_muted": "#8B93A2",

    # Accent (violet)
    "accent": "#6D4FD8",
    "accent_hover": "#5A3CC0",
    "accent_pressed": "#4D32AB",
    "accent_soft": "#EFEBFC",
    "accent_soft_hover": "#E2DBF9",
    "on_accent": "#FFFFFF",

    # Status
    "success": "#2FA66C",
    "success_soft": "#E6F6EE",
    "warning": "#D97706",
    "warning_soft": "#FBF1E0",
    "danger": "#E5484D",
    "danger_hover": "#D8373B",
    "danger_soft": "#FDEDEE",

    # Misc
    "selection": "#DDD3F8",
    "shadow_sm": "0 1px 2px rgba(24,26,34,0.05)",
    "shadow_md": "0 6px 20px rgba(24,26,34,0.08)",
    "shadow_lg": "0 18px 44px rgba(24,26,34,0.12)",
}


def token(name: str) -> str:
    return PALETTE.get(name, name)


def css_vars(extra: dict = None) -> str:
    """Return a CSS `:root { ... }` block for the shared palette."""
    src = dict(PALETTE)
    if extra:
        src.update(extra)
    lines = []
    for key, value in src.items():
        if isinstance(value, (int, float)):
            continue
        lines.append(f"    --{key}: {value};")
    return ":root {\n" + "\n".join(lines) + "\n}"


# ── Qt stylesheet ────────────────────────────────────────────────────────────
def qss() -> str:
    """The full Qt stylesheet for Rhodium's native chrome (light + violet)."""
    c = PALETTE
    return f"""
/* =========================================================
   RHODIUM — LIGHT PREMIUM UI
   ========================================================= */

* {{
    font-family: "Segoe UI", "Inter", -apple-system, BlinkMacSystemFont, "Helvetica Neue", sans-serif;
    font-size: 13px;
    outline: none;
}}

QWidget {{
    color: {c['text_primary']};
}}

QMainWindow {{
    background: {c['bg_app']};
    color: {c['text_primary']};
}}

QWidget#BrowserRoot {{
    background: {c['bg_app']};
    border: 1px solid {c['border']};
    border-radius: 10px;
}}

QWidget#BrowserSurface {{
    background: {c['bg_app']};
}}

/* =========================================================
   NAVIGATION BAR
   ========================================================= */

QToolBar#NavBar {{
    background: {c['bg_surface']};
    border: none;
    border-bottom: 1px solid {c['border']};
    padding: 6px 10px;
    spacing: 2px;
    min-height: 46px;
    max-height: 46px;
}}

/* =========================================================
   NAVIGATION BUTTONS
   ========================================================= */

QPushButton#NavBtn {{
    background: transparent;
    border: none;
    border-radius: 8px;
    color: {c['text_secondary']};
    padding: 0;
    min-width: 34px;
    min-height: 34px;
    max-width: 34px;
    max-height: 34px;
}}

QPushButton#NavBtn:hover {{
    background: {c['bg_hover']};
    color: {c['text_primary']};
}}

QPushButton#NavBtn:pressed {{
    background: {c['bg_active']};
    color: {c['text_primary']};
}}

QPushButton#NavBtn:disabled {{
    color: {c['text_muted']};
}}

QPushButton#NavBtn:checked {{
    background: {c['accent_soft']};
    color: {c['accent']};
}}

/* =========================================================
   URL BAR
   ========================================================= */

QLineEdit#UrlBar {{
    background: {c['bg_sunken']};
    color: {c['text_primary']};
    border: 1px solid transparent;
    border-radius: 10px;
    padding: 0 12px;
    font-size: 13px;
    selection-background-color: {c['selection']};
    selection-color: {c['text_primary']};
}}

QLineEdit#UrlBar:hover {{
    background: {c['bg_inset']};
    border: 1px solid {c['border_strong']};
}}

QLineEdit#UrlBar:focus {{
    background: {c['bg_surface']};
    border: 1px solid {c['accent']};
    selection-background-color: {c['selection']};
}}

/* =========================================================
   BROWSER TABS
   ========================================================= */

QWidget#BrowserTabs {{
    background: {c['bg_app']};
    border: none;
}}

QWidget#TabStrip {{
    background: {c['bg_app']};
    border-bottom: 1px solid {c['border']};
}}

QTabBar#RhodiumTabBar {{
    background: transparent;
    border: none;
    qproperty-drawBase: 0;
    min-height: 38px;
    max-height: 38px;
    font-size: 12px;
    font-weight: 500;
}}

QTabBar#RhodiumTabBar::tab {{
    background: transparent;
    color: {c['text_secondary']};
    border: none;
    border-radius: 9px;
    padding: 0 10px;
    margin-top: 4px;
    margin-bottom: 4px;
    margin-right: 3px;
    min-width: 90px;
    max-width: 220px;
    min-height: 30px;
    max-height: 30px;
}}

QTabBar#RhodiumTabBar::tab:hover {{
    background: {c['bg_hover']};
    color: {c['text_primary']};
}}

QTabBar#RhodiumTabBar::tab:selected {{
    background: {c['bg_surface']};
    color: {c['text_primary']};
    border: 1px solid {c['border']};
}}

QTabBar#RhodiumTabBar::close-button {{
    image: url(style/icons/close (2).png);
    width: 16px;
    height: 16px;
    subcontrol-position: right;
    margin-left: 4px;
    margin-right: 2px;
    border-radius: 5px;
    padding: 2px;
}}

QTabBar#RhodiumTabBar::close-button:hover {{
    background: {c['danger_soft']};
}}

QTabBar#RhodiumTabBar QToolButton {{
    background: transparent;
    border: none;
    border-radius: 6px;
    color: {c['text_secondary']};
    margin: 4px 2px;
    min-width: 22px;
    max-width: 22px;
}}

QTabBar#RhodiumTabBar QToolButton:hover {{
    background: {c['bg_hover']};
    color: {c['text_primary']};
}}

QToolButton#NewTabButton {{
    background: transparent;
    border: none;
    border-radius: 8px;
    padding: 0;
    margin-top: 4px;
    margin-bottom: 4px;
    color: {c['text_secondary']};
}}

QToolButton#NewTabButton:hover {{
    background: {c['bg_hover']};
    color: {c['text_primary']};
}}

QToolButton#NewTabButton:pressed {{
    background: {c['bg_active']};
}}

/* =========================================================
   DOWNLOADS (toolbar popup / panel)
   ========================================================= */

QToolButton#DownloadButton {{
    background: transparent;
    border: none;
    border-radius: 8px;
    padding: 0;
    margin: 0 3px;
}}

QToolButton#DownloadButton:hover {{
    background: {c['bg_hover']};
}}

QToolButton#DownloadButton:pressed {{
    background: {c['bg_active']};
}}

QFrame#DownloadPopup,
QFrame#DownloadPanel {{
    background: {c['bg_surface']};
    border: 1px solid {c['border']};
    border-radius: 12px;
}}

QLabel#PopupHeader {{
    color: {c['text_primary']};
    font-size: 13px;
    font-weight: 600;
    padding: 12px 14px;
}}

QFrame#PanelDivider {{
    background: {c['border']};
    border: none;
}}

QFrame#DownloadPopupItem {{
    background: {c['bg_surface']};
    border: 1px solid {c['border']};
    border-radius: 10px;
}}

QFrame#DownloadPopupItem:hover {{
    border-color: {c['border_strong']};
}}

QFrame#DownloadMenuRow {{
    background: transparent;
    border: none;
    border-radius: 8px;
}}

QFrame#DownloadMenuRow:hover {{
    background: {c['bg_hover']};
}}

QLabel#DownloadItemIcon {{
    background: {c['bg_sunken']};
    border-radius: 6px;
}}

QLabel#DownloadItemName {{
    color: {c['text_primary']};
    font-size: 12px;
    font-weight: 600;
}}

QLabel#DownloadItemStatus {{
    color: {c['text_secondary']};
    font-size: 11px;
}}

QLabel#DownloadItemSpeed {{
    color: {c['text_muted']};
    font-size: 11px;
}}

QProgressBar#DownloadProgressBar {{
    background: {c['bg_sunken']};
    border: none;
    border-radius: 2px;
}}

QProgressBar#DownloadProgressBar::chunk {{
    background: {c['accent']};
    border-radius: 2px;
}}

QToolButton#DownloadMiniBtn {{
    background: {c['bg_sunken']};
    color: {c['text_secondary']};
    border: none;
    border-radius: 6px;
    font-size: 12px;
}}

QToolButton#DownloadMiniBtn:hover {{
    background: {c['bg_active']};
    color: {c['text_primary']};
}}

QLabel#PanelFooter {{
    color: {c['accent']};
    font-size: 12px;
    font-weight: 600;
    padding: 12px;
    border-top: 1px solid {c['border']};
}}

QLabel#PanelFooter:hover {{
    background: {c['bg_hover']};
}}

QLabel#DownloadEmpty {{
    color: {c['text_muted']};
    font-size: 12px;
    padding: 20px;
}}

QScrollArea#DownloadScroll {{
    background: transparent;
    border: none;
}}

QFrame#DownloadPopup QScrollBar:vertical,
QFrame#DownloadPanel QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 4px 2px;
}}

QFrame#DownloadPopup QScrollBar::handle:vertical,
QFrame#DownloadPanel QScrollBar::handle:vertical {{
    background: {c['border_strong']};
    border-radius: 4px;
    min-height: 20px;
}}

QFrame#DownloadPopup QScrollBar::handle:vertical:hover,
QFrame#DownloadPanel QScrollBar::handle:vertical:hover {{
    background: {c['text_muted']};
}}

/* =========================================================
   SUGGESTION POPUP
   ========================================================= */

QFrame#SuggestionPopup {{
    background: {c['bg_surface']};
    border: 1px solid {c['border']};
    border-radius: 12px;
}}

QListWidget#SuggestionList {{
    background: transparent;
    border: none;
    outline: none;
}}

QListWidget#SuggestionList::item {{
    background: transparent;
    border-radius: 8px;
    margin: 1px 3px;
}}

QListWidget#SuggestionList::item:hover {{
    background: {c['bg_hover']};
}}

QListWidget#SuggestionList::item:selected {{
    background: {c['accent_soft']};
}}

QWidget#SuggestionRow {{
    background: transparent;
}}

QLabel#SuggestionPrimary {{
    color: {c['text_primary']};
    font-size: 12px;
    font-weight: 500;
    background: transparent;
}}

QLabel#SuggestionSecondary {{
    color: {c['text_secondary']};
    font-size: 11px;
    background: transparent;
}}

QLabel#SuggestionIcon {{
    background: transparent;
}}

/* =========================================================
   STATUS BAR
   ========================================================= */

QStatusBar {{
    background: {c['bg_surface']};
    border-top: 1px solid {c['border']};
    color: {c['text_muted']};
    min-height: 24px;
    max-height: 24px;
}}

QLabel#StatusLabel {{
    color: {c['text_muted']};
    font-size: 11px;
    padding-left: 8px;
    padding-right: 8px;
}}

/* =========================================================
   MENUS
   ========================================================= */

QMenu {{
    background: {c['bg_surface']};
    color: {c['text_primary']};
    border: 1px solid {c['border']};
    border-radius: 10px;
    padding: 6px;
    font-size: 13px;
}}

QMenu::item {{
    padding: 7px 30px 7px 14px;
    border-radius: 7px;
    margin: 1px;
}}

QMenu::item:selected {{
    background: {c['accent_soft']};
    color: {c['text_primary']};
}}

QMenu::separator {{
    height: 1px;
    background: {c['border']};
    margin: 5px 8px;
}}

QMenu::section {{
    color: {c['text_muted']};
    font-size: 10px;
    padding: 6px 14px 2px;
    font-weight: 600;
    letter-spacing: .05em;
    text-transform: uppercase;
}}

QPushButton#WinMinBtn,
QPushButton#WinMaxBtn,
QPushButton#WinCloseBtn {{
    border: none;
    background: transparent;
    color: {c['text_secondary']};
    font-size: 14px;
    border-radius: 7px;
}}

QPushButton#WinMinBtn:hover,
QPushButton#WinMaxBtn:hover {{
    background: {c['bg_hover']};
    color: {c['text_primary']};
}}

QPushButton#WinCloseBtn:hover {{
    background: {c['danger']};
    color: white;
}}

QPushButton#WinMinBtn:pressed,
QPushButton#WinMaxBtn:pressed {{
    background: {c['bg_active']};
}}

QPushButton#WinCloseBtn:pressed {{
    background: {c['danger_hover']};
}}

/* =========================================================
   DIALOGS / GENERAL CONTROLS
   ========================================================= */

QDialog {{
    background: {c['bg_surface']};
    color: {c['text_primary']};
}}

QLabel {{
    color: {c['text_primary']};
}}

QLabel#SettingsTitle {{
    color: {c['text_primary']};
    font-size: 18px;
    font-weight: 700;
    letter-spacing: -.02em;
}}

QLineEdit {{
    background: {c['bg_sunken']};
    color: {c['text_primary']};
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 6px 10px;
}}

QLineEdit:hover {{
    border-color: {c['border_strong']};
}}

QLineEdit:focus {{
    border-color: {c['accent']};
    background: {c['bg_surface']};
}}

QPushButton {{
    background: {c['bg_sunken']};
    color: {c['text_secondary']};
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 7px 14px;
    font-size: 13px;
}}

QPushButton:hover {{
    background: {c['bg_hover']};
    color: {c['text_primary']};
    border-color: {c['border']};
}}

QPushButton:pressed {{
    background: {c['bg_active']};
}}

QPushButton#PrimaryBtn {{
    background: {c['accent']};
    color: {c['on_accent']};
    font-weight: 600;
    border: none;
}}

QPushButton#PrimaryBtn:hover {{
    background: {c['accent_hover']};
    color: {c['on_accent']};
}}

QPushButton#PrimaryBtn:pressed {{
    background: {c['accent_pressed']};
}}

QCheckBox {{
    color: {c['text_secondary']};
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid {c['border_strong']};
    background: {c['bg_surface']};
}}

QCheckBox::indicator:hover {{
    border-color: {c['accent']};
}}

QCheckBox::indicator:checked {{
    background: {c['accent']};
    border-color: {c['accent']};
}}

QSpinBox,
QComboBox {{
    background: {c['bg_sunken']};
    color: {c['text_primary']};
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 5px 8px;
}}

QSpinBox:focus,
QComboBox:focus {{
    border-color: {c['accent']};
    background: {c['bg_surface']};
}}

QComboBox QAbstractItemView {{
    background: {c['bg_surface']};
    color: {c['text_primary']};
    border: 1px solid {c['border']};
    border-radius: 8px;
    selection-background-color: {c['accent_soft']};
    selection-color: {c['text_primary']};
}}

QListWidget {{
    background: {c['bg_surface']};
    color: {c['text_primary']};
    border: 1px solid {c['border']};
    border-radius: 10px;
    padding: 4px;
}}

QListWidget::item {{
    padding: 6px;
    border-radius: 7px;
}}

QListWidget::item:selected {{
    background: {c['accent_soft']};
}}

QTextEdit {{
    background: {c['bg_surface']};
    color: {c['text_primary']};
    border: 1px solid {c['border']};
    border-radius: 10px;
}}

QTextEdit:focus {{
    border-color: {c['accent']};
}}

/* =========================================================
   FIND BAR
   ========================================================= */

QFrame#FindBar {{
    background: {c['bg_surface']};
    border-top: 1px solid {c['border']};
    max-height: 44px;
}}

QLineEdit#FindInput {{
    background: {c['bg_sunken']};
    border-radius: 8px;
    padding: 5px 10px;
    max-width: 300px;
}}

QPushButton#FindClose {{
    background: transparent;
    border: none;
    border-radius: 6px;
}}

QPushButton#FindClose:hover {{
    background: {c['bg_hover']};
}}

QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 2px;
}}

QScrollBar::handle:vertical {{
    background: {c['border_strong']};
    border-radius: 5px;
    min-height: 24px;
}}

QScrollBar::handle:vertical:hover {{
    background: {c['text_muted']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QToolTip {{
    background: {c['text_primary']};
    color: {c['bg_surface']};
    border: none;
    border-radius: 6px;
    padding: 5px 8px;
    font-size: 12px;
}}
"""
