import sys
import os
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class GameLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Game Launcher")
        self.setFixedSize(400, 300)
        self.setStyleSheet("background-color: #f0f0f0;")
        self.init_ui()

        # Store base path
        self.base_path = os.path.dirname(os.path.abspath(__file__))

    def init_ui(self):
        layout = QVBoxLayout()

        # Title
        title = QLabel("Select a Game")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        # Buttons
        ttt_btn = self.create_button("🎮 Tic Tac Toe")
        rps_btn = self.create_button("✊ Rock Paper Scissors")

        ttt_btn.clicked.connect(self.launch_ttt)
        rps_btn.clicked.connect(self.launch_rps)

        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(ttt_btn)
        layout.addWidget(rps_btn)
        layout.addStretch()

        self.setLayout(layout)

    def create_button(self, text):
        btn = QPushButton(text)
        btn.setFont(QFont("Arial", 14))
        btn.setFixedHeight(50)
        btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 2px solid #aaa;
                border-radius: 12px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #d0f0ff;
                border: 2px solid #007acc;
            }
            QPushButton:pressed {
                background-color: #90e0ff;
                border: 2px solid #005f99;
                padding-left: 12px;
                padding-top: 12px;
            }
        """)
        return btn

    def launch_ttt(self):
        path = os.path.join(self.base_path, "tic_tac_toe.py")
        if os.path.exists(path):
            subprocess.Popen([sys.executable, path])
        else:
            print("❌ tic_tac_toe.py not found at", path)

    def launch_rps(self):
        path = os.path.join(self.base_path, "rps.py")
        if os.path.exists(path):
            subprocess.Popen([sys.executable, path])
        else:
            print("❌ rps.py not found at", path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GameLauncher()
    window.show()
    sys.exit(app.exec_())
