import sys
import random
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class RockPaperScissors(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Rock Paper Scissors")
        self.setFixedSize(400, 300)
        self.setStyleSheet("background-color: #f0f0f0;")

        self.player_score = 0
        self.computer_score = 0

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Rock Paper Scissors")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        self.result_label = QLabel("Make your move!")
        self.result_label.setFont(QFont("Arial", 14))
        self.result_label.setAlignment(Qt.AlignCenter)

        self.score_label = QLabel("You: 0 | Computer: 0")
        self.score_label.setFont(QFont("Arial", 12))
        self.score_label.setAlignment(Qt.AlignCenter)

        button_layout = QHBoxLayout()
        rock_btn = QPushButton("🪨 Rock")
        paper_btn = QPushButton("📄 Paper")
        scissor_btn = QPushButton("✂️ Scissors")

        for btn in [rock_btn, paper_btn, scissor_btn]:
            btn.setFixedHeight(50)
            btn.setFont(QFont("Arial", 12))
            btn.setStyleSheet("background-color: white; border-radius: 10px;")
            button_layout.addWidget(btn)

        rock_btn.clicked.connect(lambda: self.play("Rock"))
        paper_btn.clicked.connect(lambda: self.play("Paper"))
        scissor_btn.clicked.connect(lambda: self.play("Scissors"))

        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(self.result_label)
        layout.addWidget(self.score_label)
        layout.addStretch()
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def play(self, player_choice):
        computer_choice = random.choice(["Rock", "Paper", "Scissors"])
        result = self.get_result(player_choice, computer_choice)

        if result == "Win":
            self.player_score += 1
        elif result == "Lose":
            self.computer_score += 1

        self.result_label.setText(
            f"You chose {player_choice}, Computer chose {computer_choice}.\nYou {result}!"
        )
        self.score_label.setText(
            f"You: {self.player_score} | Computer: {self.computer_score}"
        )

    def get_result(self, player, computer):
        if player == computer:
            return "Draw"
        if (
            (player == "Rock" and computer == "Scissors") or
            (player == "Paper" and computer == "Rock") or
            (player == "Scissors" and computer == "Paper")
        ):
            return "Win"
        return "Lose"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RockPaperScissors()
    window.show()
    sys.exit(app.exec_())
