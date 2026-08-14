import os
import sys
from PyQt6.QtWidgets import QApplication
from rhodium.browser_window import AdvancedBrowser
from rhodium.window_filter import ResizeMoveFilter

os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--enable-smooth-scrolling"

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("RHODIUM Browser")
    app.setOrganizationName("Rhodium")
    window = AdvancedBrowser()
    # Install the Global Event Filter onto QApplication
    event_filter = ResizeMoveFilter(window)
    app.installEventFilter(event_filter)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
