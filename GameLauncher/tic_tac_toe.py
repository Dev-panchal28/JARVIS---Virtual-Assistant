import sys
import random
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QGridLayout,
    QLabel, QMessageBox, QVBoxLayout, QStackedWidget
)
from PyQt5.QtCore import Qt, QTimer, QUrl
from PyQt5.QtGui import QFont
from PyQt5.QtMultimedia import QSoundEffect


class MainMenu(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel("Tic Tac Toe")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        single_btn = QPushButton("Single Player")
        multi_btn = QPushButton("Multiplayer")

        for btn in [single_btn, multi_btn]:
            btn.setFixedHeight(50)
            btn.setFont(QFont("Arial", 14))
            btn.setStyleSheet("border-radius: 10px; background-color: #ddd;")

        single_btn.clicked.connect(self.choose_difficulty)
        multi_btn.clicked.connect(self.start_multiplayer)

        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(single_btn)
        layout.addWidget(multi_btn)
        layout.addStretch()
        self.setLayout(layout)

    def choose_difficulty(self):
        self.stacked_widget.setCurrentWidget(self.stacked_widget.difficulty_menu)

    def start_multiplayer(self):
        self.stacked_widget.game_screen.set_mode("Multiplayer")
        self.stacked_widget.setCurrentWidget(self.stacked_widget.game_screen)


class DifficultyMenu(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        label = QLabel("Select Difficulty")
        label.setFont(QFont("Arial", 18))
        label.setAlignment(Qt.AlignCenter)

        for level in ["Easy", "Medium", "Hard"]:
            btn = QPushButton(level)
            btn.setFont(QFont("Arial", 14))
            btn.setFixedHeight(40)
            btn.setStyleSheet("border-radius: 10px; background-color: #eee;")
            btn.clicked.connect(lambda _, diff=level: self.start_game(diff))
            layout.addWidget(btn)

        back_btn = QPushButton("Back")
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.stacked_widget.main_menu))
        layout.addWidget(back_btn)

        self.setLayout(layout)

    def start_game(self, difficulty):
        self.stacked_widget.game_screen.set_mode("Single", difficulty)
        self.stacked_widget.setCurrentWidget(self.stacked_widget.game_screen)


class GameScreen(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.setStyleSheet("background-color: #f5f5f5;")
        self.setFixedSize(350, 450)

        self.current_player = "X"
        self.difficulty = None
        self.mode = "Single"
        self.board = [["" for _ in range(3)] for _ in range(3)]
        self.player_score = 0
        self.computer_score = 0
        self.draws = 0
        #self.sound = QSoundEffect()
        #self.sound.setSource(QUrl.fromLocalFile("click.wav"))
        #self.sound.setVolume(0.5)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.label = QLabel("Turn: Player X")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(QFont("Arial", 16))
        self.layout.addWidget(self.label)

        self.score_label = QLabel("Wins: 0 | Losses: 0 | Draws: 0")
        self.score_label.setAlignment(Qt.AlignCenter)
        self.score_label.setFont(QFont("Arial", 12))
        self.layout.addWidget(self.score_label)

        self.grid = QGridLayout()
        self.buttons = [[QPushButton("") for _ in range(3)] for _ in range(3)]

        for i in range(3):
            for j in range(3):
                btn = self.buttons[i][j]
                btn.setFixedSize(100, 100)
                btn.setFont(QFont("Arial", 24, QFont.Bold))
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: white;
                        border: 2px solid #333;
                        border-radius: 10px;
                    }
                    QPushButton:hover {
                        background-color: #e0f7fa;
                    }
                """)
                btn.clicked.connect(lambda _, x=i, y=j: self.handle_click(x, y))
                self.grid.addWidget(btn, i, j)

        self.layout.addLayout(self.grid)

    def set_mode(self, mode, difficulty=None):
        self.mode = mode
        self.difficulty = difficulty
        self.reset_board()
        self.label.setText("Turn: You (X)" if mode == "Single" else "Turn: Player X")

    def handle_click(self, x, y):
        if self.board[x][y] != "" or (self.mode == "Single" and self.current_player != "X"):
            return

        self.make_move(x, y, self.current_player)

        if self.check_winner(self.current_player):
            msg = "You win!" if self.mode == "Single" and self.current_player == "X" else f"{self.current_player} wins!"
            self.update_score(msg)
            self.show_replay(msg)
        elif self.is_draw():
            self.update_score("draw")
            self.show_replay("It's a draw!")
        else:
            self.current_player = "O" if self.current_player == "X" else "X"
            if self.mode == "Single" and self.current_player == "O":
                self.label.setText("Turn: Computer (O)")
                QTimer.singleShot(500, self.computer_move)
            else:
                self.label.setText("Turn: Player X" if self.current_player == "X" else "Turn: Player O")

    def make_move(self, x, y, player):
        self.board[x][y] = player
        self.buttons[x][y].setText(player)
        #self.sound.play()

    def computer_move(self):
        if self.difficulty == "Easy":
            self.random_ai()
        elif self.difficulty == "Medium":
            self.medium_ai()
        elif self.difficulty == "Hard":
            self.hard_ai()

        if self.check_winner("O"):
            self.update_score("Computer wins")
            self.show_replay("Computer wins!")
        elif self.is_draw():
            self.update_score("draw")
            self.show_replay("It's a draw!")
        else:
            self.current_player = "X"
            self.label.setText("Turn: You (X)")

    def update_score(self, message):
        if self.mode == "Single":
            if "You win" in message:
                self.player_score += 1
            elif "Computer wins" in message:
                self.computer_score += 1
            elif "draw" in message.lower():
                self.draws += 1
            self.score_label.setText(f"Wins: {self.player_score} | Losses: {self.computer_score} | Draws: {self.draws}")

    def reset_board(self):
        self.current_player = "X"
        self.board = [["" for _ in range(3)] for _ in range(3)]
        for row in self.buttons:
            for btn in row:
                btn.setText("")

    def show_replay(self, message):
        box = QMessageBox(self)
        box.setWindowTitle("Game Over")
        box.setText(message)
        box.setStandardButtons(QMessageBox.Retry | QMessageBox.Close)
        ret = box.exec_()
        if ret == QMessageBox.Retry:
            self.set_mode(self.mode, self.difficulty)
        else:
            self.stacked_widget.setCurrentWidget(self.stacked_widget.main_menu)

    def is_draw(self):
        return all(cell != "" for row in self.board for cell in row)

    def check_winner(self, p):
        b = self.board
        return any(all(c == p for c in row) for row in b) or \
               any(all(b[i][j] == p for i in range(3)) for j in range(3)) or \
               all(b[i][i] == p for i in range(3)) or \
               all(b[i][2 - i] == p for i in range(3))

    def random_ai(self):
        empty = [(i, j) for i in range(3) for j in range(3) if self.board[i][j] == ""]
        if empty:
            x, y = random.choice(empty)
            self.make_move(x, y, "O")

    def medium_ai(self):
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == "":
                    self.board[i][j] = "O"
                    if self.check_winner("O"):
                        self.make_move(i, j, "O")
                        return
                    self.board[i][j] = ""
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == "":
                    self.board[i][j] = "X"
                    if self.check_winner("X"):
                        self.board[i][j] = "O"
                        self.make_move(i, j, "O")
                        return
                    self.board[i][j] = ""
        self.random_ai()

    def hard_ai(self):
        best_score = -float('inf')
        move = None
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == "":
                    self.board[i][j] = "O"
                    score = self.minimax(False)
                    self.board[i][j] = ""
                    if score > best_score:
                        best_score = score
                        move = (i, j)
        if move:
            self.make_move(*move, "O")

    def minimax(self, is_max):
        if self.check_winner("O"): return 1
        if self.check_winner("X"): return -1
        if self.is_draw(): return 0

        if is_max:
            best = -float('inf')
            for i in range(3):
                for j in range(3):
                    if self.board[i][j] == "":
                        self.board[i][j] = "O"
                        best = max(best, self.minimax(False))
                        self.board[i][j] = ""
            return best
        else:
            best = float('inf')
            for i in range(3):
                for j in range(3):
                    if self.board[i][j] == "":
                        self.board[i][j] = "X"
                        best = min(best, self.minimax(True))
                        self.board[i][j] = ""
            return best


class TicTacToeApp(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.main_menu = MainMenu(self)
        self.difficulty_menu = DifficultyMenu(self)
        self.game_screen = GameScreen(self)

        self.addWidget(self.main_menu)
        self.addWidget(self.difficulty_menu)
        self.addWidget(self.game_screen)

        self.setCurrentWidget(self.main_menu)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TicTacToeApp()
    window.setWindowTitle("Tic Tac Toe")
    window.show()
    sys.exit(app.exec_())