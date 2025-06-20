from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, QLineEdit,QGraphicsOpacityEffect,
    QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QFrame, QLabel, QSizePolicy
)
from PyQt5.QtGui import QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat
from PyQt5.QtCore import Qt, QSize, QTimer,QPropertyAnimation
from dotenv import dotenv_values
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import subprocess
import pygame
from Backend.Settings import show_settings_menu


env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname")
current_dir = os.getcwd()
old_chat_message = ""
TempDirPath = rf"{current_dir}\Frontend\Files"
GraphicsDirPath = rf"{current_dir}\Frontend\Graphics"


def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer


def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = [
        "how", "what", "who", "where", "when", "why", "which", "whose", "whom",
        "can you", "what's", "where's", "how's"
    ]

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."

    return new_query.capitalize()


def SetMicrophoneStatus(Command):
    with open(rf'{TempDirPath}\Mic.data', "w", encoding='utf-8') as file:
        file.write(Command)


def GetMicrophoneStatus():
    with open(rf'{TempDirPath}\Mic.data', "r", encoding='utf-8') as file:
        Status = file.read()
    return Status


def SetAssistantStatus(Status):
    with open(rf'{TempDirPath}\Status.data', "w", encoding='utf-8') as file:
        file.write(Status)


def GetAssistantStatus():
    with open(rf'{TempDirPath}\Status.data', "r", encoding='utf-8') as file:
        Status = file.read()
    return Status


def MicButtonInitialed():
    SetMicrophoneStatus("False")


def MicButtonClosed():
    SetMicrophoneStatus("True")


def SetWakeTriggerStatus(status):
    with open(rf'{TempDirPath}\WakeTrigger.data', "w", encoding='utf-8') as file:
        file.write(status)


def GetWakeTriggerStatus():
    try:
        with open(rf'{TempDirPath}\WakeTrigger.data', "r", encoding='utf-8') as file:
            return file.read().strip()
    except FileNotFoundError:
        return "True"  # Default to wake trigger ON

# Existing imports and code above...

def texttospeech(text):
    """
    Function to speak the given text using edge-tts or any other TTS engine.
    This example uses edge-tts via subprocess as a placeholder.
    You can replace this with your actual TTS implementation.
    """
    try:
        # Example using edge-tts CLI (you can adapt as per your TTS setup)
        # It saves to a temp mp3 and plays using ffplay or similar.
        # Here is a simple synchronous example:
        import edge_tts
        import asyncio

        async def speak(text):
            communicate = edge_tts.Communicate(text, "en-CA-LiamNeural")
            await communicate.play()

        asyncio.run(speak(text))
        
    except Exception as e:
        print(f"TTS Error: {e}")

def GetWakeTriggerEnabled():
    """
    Return True if wake trigger is enabled (wake word active).
    This reads from WakeTrigger.data file, returning True if it contains 'True'.
    """
    status = GetWakeTriggerStatus()  # You already have this function
    return status == "True"



def GraphicsDirectoryPath(Filename):
    Path = rf'{GraphicsDirPath}\{Filename}'
    return Path


def TempDirectoryPath(Filename):
    Path = rf'{TempDirPath}\{Filename}'
    return Path


def ShowTextToScreen(Text):
    with open(rf'{TempDirPath}\Responses.data', "w", encoding='utf-8') as file:
        file.write(Text)


class ChatSection(QWidget):

    def __init__(self):
        super(ChatSection, self).__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(-10, 40, 40, 100)
        layout.setSpacing(-100)
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        layout.addWidget(self.chat_text_edit)
        self.setStyleSheet("background-color: black;")
        layout.setSizeConstraint(QVBoxLayout.SetDefaultConstraint)
        layout.setStretch(1, 1)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        text_color = QColor(Qt.blue)
        text_color_text = QTextCharFormat()
        text_color_text.setForeground(text_color)
        self.chat_text_edit.setCurrentCharFormat(text_color_text)
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        movie = QMovie(GraphicsDirectoryPath('Jarvis.gif'))
        max_gif_size_W = 480
        max_gif_size_H = 270
        movie.setScaledSize(QSize(max_gif_size_W, max_gif_size_H))
        self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.gif_label.setMovie(movie)
        movie.start()
        layout.addWidget(self.gif_label)
        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size:16px; margin-right: 195px; border: none; margin-top: -30px;")
        self.label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.label)
        layout.setSpacing(-10)
        layout.addWidget(self.gif_label)
        font = QFont()
        font.setPointSize(13)
        self.chat_text_edit.setFont(font)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(5)
        self.chat_text_edit.viewport().installEventFilter(self)
        self.setStyleSheet("""
              QScrollBar:vertical {
              border: none;
              background: black;
              width: 10px;
              margin: 0px 0px 0px 0px;        
              }
                       
              QScrollBar::handle:vertical {
              background: white;
              min-height: 20px;
              }
            
              QScrollBar::add-line:vertical {
              background: black;
              subcontrol-position: bottom;
              subcontrol-origin: margin;
              height: 10px;
              }
            
              QCrollBar::sub-line:vertical {
              background: black;
              subcontrol-position: top;
              subcontrol-origin: margin;
              height: 10px;
              }
                           
              QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
              border: none;
              background: none;
              color: none;
              }
                           
              QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
              background: none;
              }
        """)

    def loadMessages(self):
        global old_chat_message

        with open(TempDirectoryPath('Responses.data'), "r", encoding='utf-8') as file:
            messages = file.read()

            if messages is None or len(messages) <= 1:
                pass
            elif str(old_chat_message) == str(messages):
                pass
            else:
                self.addMessage(message=messages, color='White')
                old_chat_message = messages

    def SpeechRecogText(self):
        with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
            messages = file.read()
            self.label.setText(messages)

    def load_icon(self, path, width=60, height=60):
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height)
        self.icon_label.setPixmap(new_pixmap)

    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('voice.png'), 60, 60)
            MicButtonInitialed()
        else:
            self.load_icon(GraphicsDirectoryPath('mic.png'), 60, 60)
            MicButtonClosed()

        self.toggled = not self.toggled

    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        format = QTextCharFormat()
        formatm = QTextBlockFormat()
        formatm.setTopMargin(10)
        formatm.setLeftMargin(10)
        format.setForeground(QColor(color))
        cursor.setCharFormat(format)
        cursor.setBlockFormat(formatm)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)

class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        self.settings_window = None
        self.toggled = True
        self.game_launcher_process = None

        # === MAIN LAYOUT ===
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 150)

        # === GIF ANIMATION ===
        gif_label = QLabel()
        movie = QMovie(GraphicsDirectoryPath('Jarvis.gif'))
        gif_label.setMovie(movie)
        movie.setScaledSize(QSize(screen_width, int(screen_width / 16 * 9)))
        gif_label.setAlignment(Qt.AlignCenter)
        movie.start()
        gif_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # === TRANSCRIPT LABEL ===
        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size:16px;")
        self.label.setAlignment(Qt.AlignCenter)

        # === ICONS ===
        self.icon_label = QLabel()
        mic_icon_path = GraphicsDirectoryPath('Mic_on.png') if GetWakeTriggerStatus() == "True" else GraphicsDirectoryPath('Mic_off.png')
        self.load_icon(mic_icon_path)
        self.icon_label.setFixedSize(150, 150)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.mousePressEvent = self.toggle_icon

        self.gif_button = QLabel()
        self.gif_static_icon = QPixmap(GraphicsDirectoryPath('snap_still.png')).scaled(60, 60)
        self.gif_button.setPixmap(self.gif_static_icon)
        self.gif_button.setFixedSize(150, 150)
        self.gif_button.setAlignment(Qt.AlignCenter)
        self.gif_button.mousePressEvent = self.play_gif_and_exit

        self.left_button = QLabel()
        self.left_button_icon = QPixmap(GraphicsDirectoryPath('games.png')).scaled(60, 60)
        self.left_button.setPixmap(self.left_button_icon)
        self.left_button.setFixedSize(150, 150)
        self.left_button.setAlignment(Qt.AlignCenter)
        self.left_button.mousePressEvent = self.launch_game_launcher

        # === ICON LAYOUT ===
        icon_layout = QHBoxLayout()
        icon_layout.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(self.left_button)
        icon_layout.addWidget(self.icon_label)
        icon_layout.addWidget(self.gif_button)

        # === ADD TO MAIN LAYOUT ===
        content_layout.addWidget(gif_label)
        content_layout.addWidget(self.label)
        content_layout.addLayout(icon_layout)

        self.setLayout(content_layout)
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        self.setStyleSheet("background-color: black;")

        # === TIMER ===
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(5)

        # === SETTINGS BUTTON ===
        self.settings_button = QPushButton(self)
        settings_icon = QIcon(GraphicsDirectoryPath('Settings.png'))
        self.settings_button.setIcon(settings_icon)
        self.settings_button.setIconSize(QSize(60, 60))
        self.settings_button.setStyleSheet("background-color: transparent; border: none;")
        self.settings_button.setFixedSize(60, 60)
        self.settings_button.clicked.connect(lambda: show_settings_menu(self.settings_button))

        QTimer.singleShot(0, self.position_settings_icon)

    def position_settings_icon(self):
        self.settings_button.move(self.width() - 80, 20)

    def SpeechRecogText(self):
        with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
            messages = file.read()
            self.label.setText(messages)

    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('Mic_off.png'))
            MicButtonClosed()
            SetWakeTriggerStatus("False")
        else:
            self.load_icon(GraphicsDirectoryPath('Mic_on.png'))
            MicButtonInitialed()
            SetWakeTriggerStatus("True")
        self.toggled = not self.toggled

    def load_icon(self, path):
        pixmap = QPixmap(path).scaled(60, 60)
        self.icon_label.setPixmap(pixmap)

    def play_gif_and_exit(self, event=None):
        self.movie = QMovie(GraphicsDirectoryPath('snap.gif'))
        self.movie.setScaledSize(QSize(60, 60))
        self.gif_button.setMovie(self.movie)
        self.movie.start()

        try:
            pygame.mixer.init()
            pygame.mixer.music.load("Data/snap.mp3")
            pygame.mixer.music.play()
        except Exception as e:
            print(f"[Startup Sound] Failed to play snap.mp3: {e}")

        QTimer.singleShot(1500, self.flash_and_exit)

    def flash_and_exit(self):
        self.overlay = QWidget(self)
        self.overlay.setStyleSheet("background-color: white;")
        self.overlay.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.overlay.setGeometry(0, 0, self.width(), self.height())

        self.opacity_effect = QGraphicsOpacityEffect()
        self.overlay.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(0)
        self.overlay.show()

        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(1000)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

        self.animation.finished.connect(QApplication.quit)

    def launch_game_launcher(self, event):
        self.setWindowTitle("Game Launcher")
        if self.game_launcher_process is None or self.game_launcher_process.poll() is not None:
            script_path = os.path.join(os.getcwd(), "GameLauncher", "launcher.py")
            if os.path.exists(script_path):
                self.game_launcher_process = subprocess.Popen([sys.executable, script_path])
            else:
                print("launcher.py not found.")
        else:
            try:
                import pygetwindow as gw
                for w in gw.getWindowsWithTitle("Game Launcher"):
                    if w.isMinimized:
                        w.restore()
                        w.activate()
            except Exception as e:
                print("Could not focus Game Launcher window:", e)






class MessageScreen(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        layout = QVBoxLayout()
        label = QLabel("")
        layout.addWidget(label)
        chat_section = ChatSection()
        layout.addWidget(chat_section)
        self.setLayout(layout)
        self.setStyleSheet("background-color: black;")
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)


class CustomTopBar(QWidget):

    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.initUI()
        self.current_screen = None
        self.stacked_widget = stacked_widget

    def initUI(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignRight)
        home_button = QPushButton()
        home_icon = QIcon(GraphicsDirectoryPath("Home.png"))
        home_button.setIcon(home_icon)
        home_button.setText(" Home")
        home_button.setStyleSheet("height:40px; line-height:40px ; background-color:white ; color: black")
        message_button = QPushButton()
        message_icon = QIcon(GraphicsDirectoryPath("Chats.png"))
        message_button.setIcon(message_icon)
        message_button.setText(" Chat")
        message_button.setStyleSheet("height:40px; line-height:40px; background-color:white ; color: black")
        minimize_button = QPushButton()
        minimize_icon = QIcon(GraphicsDirectoryPath('Minimize2.png'))
        minimize_button.setIcon(minimize_icon)
        minimize_button.setStyleSheet("background-color:white")
        minimize_button.clicked.connect(self.minimizeWindow)
        self.maximize_button = QPushButton()
        self.maximize_icon = QIcon(GraphicsDirectoryPath('Maximize.png'))
        self.restore_icon = QIcon(GraphicsDirectoryPath('Minimize.png'))
        self.maximize_button.setIcon(self.maximize_icon)
        self.maximize_button.setFlat(True)
        self.maximize_button.setStyleSheet("background-color:white")
        self.maximize_button.clicked.connect(self.maximizeWindow)
        close_button = QPushButton()
        close_icon = QIcon(GraphicsDirectoryPath('Close.png'))
        close_button.setIcon(close_icon)
        close_button.setStyleSheet("background-color:white")
        close_button.clicked.connect(self.closeWindow)
        line_frame = QFrame()
        line_frame.setFixedHeight(1)
        line_frame.setFrameShape(QFrame.HLine)
        line_frame.setFrameShadow(QFrame.Sunken)
        line_frame.setStyleSheet("border-color: black;")
        title_label = QLabel(f" {str(Assistantname).capitalize()} AI    ")
        title_label.setStyleSheet("color: black; font-size: 18px;; background-color:white")
        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        message_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        layout.addWidget(title_label)
        layout.addStretch(1)
        layout.addWidget(home_button)
        layout.addWidget(message_button)
        layout.addStretch(1)
        layout.addWidget(minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(close_button)
        layout.addWidget(line_frame)
        self.draggable = True
        self.offset = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.white)
        super().paintEvent(event)

    def minimizeWindow(self):
        self.parent().showMinimized()

    def maximizeWindow(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.maximize_button.setIcon(self.maximize_icon)
        else:
            self.parent().showMaximized()
            self.maximize_button.setIcon(self.restore_icon)

    def closeWindow(self):
        self.parent().close()

    def mousePressEvent(self, event):
        if self.draggable:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.draggable and self.offset:
            new_pos = event.globalPos() - self.offset
            self.parent().move(new_pos)

    def showMessageScreen(self):
        if self.current_screen is not None:
            self.current_screen.hide()

        message_screen = MessageScreen(self)
        layout = self.parent().layout()
        if layout is not None:
            layout.addWidget(message_screen)
        self.current_screen = message_screen

    def showInitialScreen(self):
        if self.current_screen is not None:
            self.current_screen.hide()

        initial_screen = InitialScreen(self)
        layout = self.parent().layout()
        if layout is not None:
            layout.addWidget(initial_screen)
        self.current_screen = initial_screen


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()

    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        stacked_widget = QStackedWidget(self)
        initial_screen = InitialScreen()
        message_screen = MessageScreen()
        stacked_widget.addWidget(initial_screen)
        stacked_widget.addWidget(message_screen)
        self.setGeometry(0, 0, screen_width, screen_height)
        self.setStyleSheet("background-color: black;")
        top_bar = CustomTopBar(self, stacked_widget)
        self.setMenuWidget(top_bar)
        self.setCentralWidget(stacked_widget)


def GraphicalUserInterface():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    return app,window


if __name__ == "__main__":
    GraphicalUserInterface()
