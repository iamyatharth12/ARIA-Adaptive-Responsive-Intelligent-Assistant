import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout,
    QVBoxLayout, QListWidget, QTextEdit, QLineEdit,
    QPushButton, QLabel, QListWidgetItem, QSplitter
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor

from memory import load_memory, add_message, new_conv_id, get_messages, get_title
from commands import handle_command

# ─────────────────────────────────────────────
#  STYLES
# ─────────────────────────────────────────────
MAIN_STYLE = """
QMainWindow, QWidget#root {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 #0f0f0f, stop:1 #1a1a1a);
}
QWidget {
    background: transparent;
    color: #e0e0e0;
    font-family: 'Segoe UI', sans-serif;
    font-size: 14px;
}
QSplitter::handle { background: #2a2a2a; width: 1px; }
"""

SIDEBAR_STYLE = """
QListWidget {
    background: rgba(255,255,255,0.04);
    border: none;
    border-right: 1px solid #2a2a2a;
    border-radius: 0px;
    padding: 8px 4px;
    color: #aaaaaa;
    font-size: 13px;
}
QListWidget::item {
    padding: 10px 14px;
    border-radius: 8px;
    margin: 2px 6px;
}
QListWidget::item:selected {
    background: rgba(255,255,255,0.10);
    color: #ffffff;
}
QListWidget::item:hover {
    background: rgba(255,255,255,0.06);
}
"""

CHAT_STYLE = """
QTextEdit {
    background: transparent;
    border: none;
    color: #e0e0e0;
    font-size: 14px;
    padding: 12px;
    line-height: 1.6;
}
"""

INPUT_STYLE = """
QLineEdit {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 14px;
    padding: 12px 18px;
    color: #ffffff;
    font-size: 14px;
}
QLineEdit:focus {
    border: 1px solid rgba(255,255,255,0.25);
    background: rgba(255,255,255,0.10);
}
"""

BTN_NEW_STYLE = """
QPushButton {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 10px;
    color: #cccccc;
    padding: 8px 14px;
    font-size: 13px;
}
QPushButton:hover {
    background: rgba(255,255,255,0.14);
    color: #ffffff;
}
"""

BTN_SEND_STYLE = """
QPushButton {
    background: rgba(255,255,255,0.10);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 12px;
    color: #ffffff;
    padding: 10px 22px;
    font-size: 14px;
    font-weight: 600;
}
QPushButton:hover {
    background: rgba(255,255,255,0.18);
}
"""

LABEL_STYLE = "color: #555555; font-size: 12px; padding: 8px 14px;"

# ─────────────────────────────────────────────
#  MAIN WINDOW
# ─────────────────────────────────────────────
class ARIAWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ARIA")
        self.setMinimumSize(860, 560)
        self.current_conv_id = new_conv_id()

        self.setStyleSheet(MAIN_STYLE)
        self._build_ui()
        self._load_sidebar()

    def _build_ui(self):
        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)

        # ── Sidebar ──
        sidebar = QWidget()
        sidebar.setFixedWidth(210)
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(0, 12, 0, 12)
        sb_layout.setSpacing(6)

        aria_label = QLabel("  ◈ ARIA")
        aria_label.setStyleSheet("color:#ffffff; font-size:16px; font-weight:700; padding:8px 14px 12px;")
        sb_layout.addWidget(aria_label)

        self.btn_new = QPushButton("+ New Chat")
        self.btn_new.setStyleSheet(BTN_NEW_STYLE)
        self.btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_new.clicked.connect(self._new_conversation)
        sb_layout.addWidget(self.btn_new)

        hist_label = QLabel("History")
        hist_label.setStyleSheet(LABEL_STYLE)
        sb_layout.addWidget(hist_label)

        self.sidebar_list = QListWidget()
        self.sidebar_list.setStyleSheet(SIDEBAR_STYLE)
        self.sidebar_list.itemClicked.connect(self._load_conversation)
        sb_layout.addWidget(self.sidebar_list)

        splitter.addWidget(sidebar)

        # ── Chat Area ──
        chat_widget = QWidget()
        chat_layout = QVBoxLayout(chat_widget)
        chat_layout.setContentsMargins(20, 16, 20, 16)
        chat_layout.setSpacing(10)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet(CHAT_STYLE)
        chat_layout.addWidget(self.chat_display)

        # Input row
        input_row = QHBoxLayout()
        input_row.setSpacing(10)

        self.input_box = QLineEdit()
        self.input_box.setPlaceholderText("Type a command...  (open chrome / play lofi / search python)")
        self.input_box.setStyleSheet(INPUT_STYLE)
        self.input_box.returnPressed.connect(self._handle_input)

        send_btn = QPushButton("Send")
        send_btn.setStyleSheet(BTN_SEND_STYLE)
        send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        send_btn.clicked.connect(self._handle_input)

        input_row.addWidget(self.input_box)
        input_row.addWidget(send_btn)
        chat_layout.addLayout(input_row)

        splitter.addWidget(chat_widget)
        splitter.setSizes([210, 650])

        layout.addWidget(splitter)

        self._append_message("aria", "Hey. I'm ARIA. Tell me what to do.")

    # ─────────────────────────────────────────
    #  SIDEBAR HELPERS
    # ─────────────────────────────────────────
    def _load_sidebar(self):
        self.sidebar_list.clear()
        for conv in load_memory():
            title = conv.get("title", conv["id"])
            item = QListWidgetItem(title)
            item.setData(Qt.ItemDataRole.UserRole, conv["id"])
            self.sidebar_list.addItem(item)

    def _load_conversation(self, item):
        conv_id = item.data(Qt.ItemDataRole.UserRole)
        self.current_conv_id = conv_id
        self.chat_display.clear()
        for msg in get_messages(conv_id):
            self._append_message(msg["role"], msg["text"])

    def _new_conversation(self):
        self.current_conv_id = new_conv_id()
        self.chat_display.clear()
        self._append_message("aria", "New session. What do you need?")

    # ─────────────────────────────────────────
    #  MESSAGE HANDLING
    # ─────────────────────────────────────────
    def _handle_input(self):
        text = self.input_box.text().strip()
        if not text:
            return

        self.input_box.clear()
        self._append_message("user", text)
        add_message(self.current_conv_id, "user", text)

        response = handle_command(text)

        self._append_message("aria", response)
        add_message(self.current_conv_id, "aria", response)

        self._load_sidebar()

    def _append_message(self, role: str, text: str):
        if role == "user":
            color = "#ffffff"
            prefix = "You"
            align = "right"
            bg = "rgba(255,255,255,0.07)"
        else:
            color = "#a0c4ff"
            prefix = "ARIA"
            align = "left"
            bg = "rgba(255,255,255,0.04)"

        html = f"""
        <div style='text-align:{align}; margin:12px 0;'>
            <span style='color:#555555; font-size:11px; letter-spacing:1px;'>{prefix}</span><br>
            <span style='
                display:inline-block;
                background:{bg};
                color:{color};
                border-radius:12px;
                padding:10px 16px;
                margin-top:4px;
                max-width:78%;
                font-size:15px;
                line-height:1.7;
                border:1px solid rgba(255,255,255,0.06);
            '>{text}</span>
        </div>
        """
        self.chat_display.append(html)


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 13))
    window = ARIAWindow()
    window.show()
    sys.exit(app.exec())
