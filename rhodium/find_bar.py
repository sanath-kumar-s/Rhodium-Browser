from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox
from PyQt6.QtCore import pyqtSignal
from rhodium.utils import icon

class FindBar(QFrame):
    find_next_signal = pyqtSignal(str, bool)
    close_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("FindBar")
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(8)

        search_lbl = QLabel()
        search_lbl.setPixmap(icon("search.png").pixmap(16, 16))
        layout.addWidget(search_lbl)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Find in page…")
        self.search_input.setObjectName("FindInput")
        self.search_input.returnPressed.connect(self.on_find_next)
        layout.addWidget(self.search_input)

        self.btn_prev = QPushButton("↑")
        self.btn_prev.setFixedWidth(30)
        self.btn_prev.setToolTip("Previous match")
        self.btn_prev.clicked.connect(self.on_find_prev)
        layout.addWidget(self.btn_prev)

        self.btn_next = QPushButton("↓")
        self.btn_next.setFixedWidth(30)
        self.btn_next.setToolTip("Next match")
        self.btn_next.clicked.connect(self.on_find_next)
        layout.addWidget(self.btn_next)

        self.case_check = QCheckBox("Aa")
        self.case_check.setToolTip("Case sensitive")
        layout.addWidget(self.case_check)

        self.btn_close = QPushButton()
        self.btn_close.setIcon(icon("find-close.png"))
        self.btn_close.setFixedSize(24, 24)
        self.btn_close.setFlat(True)
        self.btn_close.setObjectName("FindClose")
        self.btn_close.clicked.connect(self.close_signal.emit)
        layout.addWidget(self.btn_close)

    def on_find_next(self):
        text = self.search_input.text()
        if text:
            self.find_next_signal.emit(text, False)

    def on_find_prev(self):
        text = self.search_input.text()
        if text:
            self.find_next_signal.emit(text, True)
