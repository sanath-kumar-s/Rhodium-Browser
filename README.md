# RHODIUM Browser

<p align="center">
  <img src="style/icons/home.png" alt="RHODIUM" width="96" />
</p>

<p align="center">
  A modern, lightweight web browser built with Python and PyQt6 WebEngine.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/PyQt6-6.6.1-41cd52?style=for-the-badge&logo=qt&logoColor=white" alt="PyQt6" />
  <img src="https://img.shields.io/badge/Platform-Windows-lightgrey?style=for-the-badge&logo=windows&logoColor=white" alt="Platform" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License" />
  <img src="https://img.shields.io/badge/Status-Active-success?style=for-the-badge" alt="Status" />
</p>

---

## 🌐 Overview

**RHODIUM Browser** is a from-scratch desktop web browser written in Python. It uses
the Chromium-powered **PyQt6 WebEngine** rendering engine to deliver a fast, familiar
browsing experience with a custom chrome (title bar, tabs, toolbar) and a rich set of
built-in features — no external browser required.

## ✨ Features

| Feature | Description |
| --- | --- |
| 🗂️ **Tabbed Browsing** | Multiple tabs with pin, reorder, close-others/right, and "all tabs" overview. |
| 🏠 **Speed-Dial Home** | Customizable shortcut tiles (add / edit / delete) with favicons. |
| 🔖 **Bookmarks** | Save, manage, and open bookmarks with filled/empty indicators. |
| 🕘 **History** | Auto-recorded browsing history with a searchable menu and clear option. |
| ⬇️ **Downloads Manager** | Full download UI with progress, pause/resume/cancel, file-type icons, and history. |
| 🔍 **Find in Page** | In-page search bar with next/previous navigation. |
| 🔎 **Address Suggestions** | Live URL/bookmark/history suggestions as you type. |
| 🔐 **Security Indicator** | Visual secure/warning indicator reflecting the current page's scheme. |
| 🔧 **DevTools Info** | Inspect page information and developer tools. |
| ⚙️ **Settings Dialog** | Persistent user settings stored per-profile. |
| 🔍 **Zoom** | Per-view zoom in / out / reset. |
| 🖥️ **Custom Window Frame** | Custom minimize/maximize/restore/close controls and smooth scrolling. |
| 💾 **Local Database** | SQLite-backed storage for history, bookmarks, shortcuts, and downloads. |

## 📸 Screenshots

> Screenshots coming soon.

## 🚀 Getting Started

### Prerequisites

- Python **3.11 or newer**
- Windows (the custom window controls target the Windows platform)

### Installation

Clone the repository and install the dependencies:

```bash
git clone <your-repo-url> RhodiumBrowser
cd RhodiumBrowser

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
```

### Running

```bash
python main.py
```

## 📦 Dependencies

| Package | Version |
| --- | --- |
| `PyQt6` | `6.6.1` |
| `PyQt6-WebEngine` | `6.6.0` |
| `PyQtWebEngine` | `5.15.6` |

## 🗂️ Project Structure

```
RhodiumBrowser/
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
├── rhodium/
│   ├── browser_window.py    # Main window, tabs, toolbar, menus
│   ├── web_views.py         # Web view/engine wrappers
│   ├── database.py          # SQLite storage (history, bookmarks, downloads)
│   ├── download_manager.py  # Download logic
│   ├── download_ui.py       # Downloads page UI
│   ├── suggestions.py       # Address/search suggestions
│   ├── suggestion_popup.py  # Suggestion popup widget
│   ├── settings_dialog.py   # Settings UI
│   ├── find_bar.py          # In-page find bar
│   ├── window_filter.py     # Global resize/move event filter
│   ├── resources.py         # Embedded resources
│   └── utils.py             # Helpers
└── style/
    └── icons/               # Application & UI icons
```

## ⌨️ Keyboard Shortcuts

A configurable shortcut list is available from the **Help → Keyboard Shortcuts**
menu inside the application.

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<p align="center">
  Made with ❤️ and PyQt6 · RHODIUM Browser
</p>
