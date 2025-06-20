from PyQt5.QtWidgets import (
    QMenu, QAction, QInputDialog, QApplication, QLineEdit, QMessageBox
)
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL

# ===== CUSTOM AUTH MANAGER =====
from Backend.auth_manager import register_user, verify_user, load_usernames

# ===== SETTINGS CLASSES =====
class AudioSettings:
    def __init__(self):
        self.volume_muted = False

class VisualSettings:
    def __init__(self):
        self.theme = "Dark"

class AccountSettings:
    def __init__(self):
        self.logged_in = False
        self.username = ""

# ===== SETTINGS MANAGER =====
class SettingsManager:
    def __init__(self):
        self.audio = AudioSettings()
        self.visual = VisualSettings()
        self.account = AccountSettings()

    def update(self, category: str, key: str, value):
        section = getattr(self, category, None)
        if section and hasattr(section, key):
            setattr(section, key, value)
            return True
        return False

settings_manager = SettingsManager()

# ===== HELPER FUNCTIONS =====
def apply_theme_to_app(theme: str):
    app = QApplication.instance()
    if app:
        if theme == "Dark":
            app.setStyleSheet("QWidget { background-color: #121212; color: white; }")
        else:
            app.setStyleSheet("QWidget { background-color: white; color: black; }")

def set_system_mute(mute: bool):
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMute(1 if mute else 0, None)
    settings_manager.update("audio", "volume_muted", mute)

def get_menu_stylesheet(theme: str):
    return """
    QMenu {{
        background-color: {};
        color: {};
        border: 1px solid {};
        font-size: 16px;
        padding: 8px;
        min-width: 220px;
    }}
    QMenu::item {{
        padding: 10px 20px;
        height: 30px;
    }}
    QMenu::item:selected {{
        background-color: {};
    }}
    """.format(
        "#1e1e1e" if theme == "Dark" else "#ffffff",
        "white" if theme == "Dark" else "black",
        "#444" if theme == "Dark" else "#aaa",
        "#3a3a3a" if theme == "Dark" else "#e0e0e0"
    )

def themed_input_dialog(parent, title, label):
    dialog = QInputDialog(parent)
    dialog.setWindowTitle(title)
    dialog.setLabelText(label)
    theme = settings_manager.visual.theme
    if theme == "Dark":
        dialog.setStyleSheet("""
            QInputDialog, QLabel {
                background-color: #121212;
                color: white;
            }
            QLineEdit {
                background-color: white;
                color: black;
            }
        """)
    else:
        dialog.setStyleSheet("""
            QInputDialog, QLabel {
                background-color: white;
                color: black;
            }
            QLineEdit {
                background-color: white;
                color: black;
            }
        """)
    ok = dialog.exec_()
    return dialog.textValue(), ok

def show_message_box(parent, title, text, icon=QMessageBox.Information):
    msg_box = QMessageBox(parent)
    msg_box.setIcon(icon)
    msg_box.setWindowTitle(title)
    msg_box.setText(text)

    theme = settings_manager.visual.theme
    if theme == "Dark":
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #121212;
                color: white;
                font-size: 14px;
            }
            QPushButton {
                background-color: #2e2e2e;
                color: white;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #3c3c3c;
            }
        """)
    else:
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: white;
                color: black;
                font-size: 14px;
            }
            QPushButton {
                background-color: #f0f0f0;
                color: black;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
    msg_box.exec_()

# ===== MAIN SETTINGS MENU =====
def show_settings_menu(parent_button):
    current_theme = settings_manager.visual.theme
    main_menu = QMenu(parent_button)
    main_menu.setStyleSheet(get_menu_stylesheet(current_theme))

    # ===== Volume Submenu =====
    volume_menu = QMenu("Volume Setting")
    volume_menu.setStyleSheet(get_menu_stylesheet(current_theme))

    mute_action = QAction("Mute", volume_menu)
    mute_action.triggered.connect(lambda: set_system_mute(True))

    unmute_action = QAction("Unmute", volume_menu)
    unmute_action.triggered.connect(lambda: set_system_mute(False))

    volume_menu.addAction(mute_action)
    volume_menu.addAction(unmute_action)

    # ===== Account Submenu =====
    account_menu = QMenu("Account")
    account_menu.setStyleSheet(get_menu_stylesheet(current_theme))

    signup_action = QAction("Signup", account_menu)
    def signup():
        username, ok = themed_input_dialog(parent_button, "Signup", "Enter new username:")
        if ok and username:
            if username in load_usernames():
                show_message_box(parent_button, "Signup Failed", f"The username '{username}' is already registered.", QMessageBox.Warning)
                return
            success = register_user(username)
            if success:
                settings_manager.update("account", "username", username)
                settings_manager.update("account", "logged_in", True)
                show_message_box(parent_button, "Signup", f"Signed up and logged in as: {username}", QMessageBox.Information)
            else:
                show_message_box(parent_button, "Signup Failed", "Username already registered or capture failed.", QMessageBox.Warning)
    signup_action.triggered.connect(signup)

    login_action = QAction("Login", account_menu)
    def login():
        if settings_manager.account.logged_in:
            show_message_box(
                parent_button,
                "Already Logged In",
                f"You're already logged in as '{settings_manager.account.username}'. Please log out first to switch accounts.",
                QMessageBox.Warning
            )
            return

        username, ok = themed_input_dialog(parent_button, "Login", "Enter your username:")
        if ok and username:
            if verify_user(username):
                settings_manager.update("account", "username", username)
                settings_manager.update("account", "logged_in", True)
                show_message_box(parent_button, "Login", f"Logged in successfully as: {username}", QMessageBox.Information)
            else:
                show_message_box(parent_button, "Login Failed", "Authentication failed. Try again.", QMessageBox.Warning)
    login_action.triggered.connect(login)

    logout_action = QAction("Logout", account_menu)
    def logout():
        if settings_manager.account.logged_in:
            settings_manager.update("account", "username", "")
            settings_manager.update("account", "logged_in", False)
            show_message_box(parent_button, "Logout", "You have been logged out.", QMessageBox.Information)
    logout_action.triggered.connect(logout)

    # Enable/Disable login/logout depending on current state
    login_action.setEnabled(not settings_manager.account.logged_in)
    logout_action.setEnabled(settings_manager.account.logged_in)

    account_menu.addAction(signup_action)
    account_menu.addAction(login_action)
    account_menu.addAction(logout_action)

    # ===== Add submenus to main menu =====
    main_menu.addMenu(volume_menu)
    main_menu.addMenu(account_menu)

    # ===== Show the menu =====
    main_menu.exec_(parent_button.mapToGlobal(parent_button.rect().bottomRight()))
