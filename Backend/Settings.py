# === Imports ===
from PyQt5.QtWidgets import (
    QMenu, QAction, QInputDialog, QApplication, QLineEdit, QMessageBox
)
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL

# === Custom Authentication Manager ===
from Backend.auth_manager import (
    signup_flow as register_user,
    login_flow as verify_user,
    load_usernames,
    set_active_user,
    clear_active_user,
    get_active_user
)

# === Settings Classes ===

class AudioSettings:
    def __init__(self):
        self.volume_muted = False  # Tracks mute state

class AccountSettings:
    def __init__(self):
        self.logged_in = bool(get_active_user())  # True if user is logged in
        self.username = get_active_user() or ""   # Store logged-in username

# === Global Settings Manager ===

class SettingsManager:
    def __init__(self):
        self.audio = AudioSettings()
        self.account = AccountSettings()

    def update(self, category: str, key: str, value):
        """Dynamically update settings values."""
        section = getattr(self, category, None)
        if section and hasattr(section, key):
            setattr(section, key, value)
            return True
        return False

# Create global instance
settings_manager = SettingsManager()

# === Audio Control Function ===

def set_system_mute(mute: bool):
    """Mute or unmute the system volume using pycaw."""
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volume.SetMute(1 if mute else 0, None)
    settings_manager.update("audio", "volume_muted", mute)

# === Theming & Styling ===

def get_menu_stylesheet():
    """Dark theme style for all menus."""
    return """
    QMenu {
        background-color: #1e1e1e;
        color: white;
        border: 1px solid #444;
        font-size: 16px;
        padding: 8px;
        min-width: 220px;
    }
    QMenu::item {
        padding: 10px 20px;
        height: 30px;
    }
    QMenu::item:selected {
        background-color: #3a3a3a;
    }
    """

def themed_input_dialog(parent, title, label):
    """Create a dark-themed input dialog."""
    dialog = QInputDialog(parent)
    dialog.setWindowTitle(title)
    dialog.setLabelText(label)
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
    ok = dialog.exec_()
    return dialog.textValue(), ok

def show_message_box(parent, title, text, icon=QMessageBox.Information):
    """Display a styled message box."""
    msg_box = QMessageBox(parent)
    msg_box.setIcon(icon)
    msg_box.setWindowTitle(title)
    msg_box.setText(text)
    msg_box.setStyleSheet("""
        QMessageBox {
            background-color: #121212;
            color: white;
            font-size: 14px;
        }
        QLabel {
            color: white;
            qproperty-alignment: AlignCenter;
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
    msg_box.exec_()

# === Main Settings Menu ===

def show_settings_menu(parent_button, profile_callback=None):
    """Build and show the settings menu."""
    main_menu = QMenu(parent_button)
    main_menu.setStyleSheet(get_menu_stylesheet())

    # === Volume Submenu ===
    volume_menu = QMenu("Volume Setting")
    volume_menu.setStyleSheet(get_menu_stylesheet())

    mute_action = QAction("Mute", volume_menu)
    mute_action.triggered.connect(lambda: set_system_mute(True))

    unmute_action = QAction("Unmute", volume_menu)
    unmute_action.triggered.connect(lambda: set_system_mute(False))

    volume_menu.addAction(mute_action)
    volume_menu.addAction(unmute_action)

    # === Account Submenu ===
    account_menu = QMenu("Account")
    account_menu.setStyleSheet(get_menu_stylesheet())

    # --- Signup Action ---
    signup_action = QAction("Signup", account_menu)
    def signup():
        username, ok = themed_input_dialog(parent_button, "Signup", "Enter new username:")
        if ok and username:
            if username in load_usernames():
                show_message_box(parent_button, "Signup Failed", f"The username '{username}' is already registered.", QMessageBox.Warning)
                return
            success = register_user(username)
            if success:
                set_active_user(username)
                settings_manager.update("account", "username", username)
                settings_manager.update("account", "logged_in", True)
                if profile_callback:
                    profile_callback(username)
                show_message_box(parent_button, "Signup", f"Signed up and logged in as: {username}", QMessageBox.Information)
            else:
                show_message_box(parent_button, "Signup Failed", "Username already registered or capture failed.", QMessageBox.Warning)
    signup_action.triggered.connect(signup)

    # --- Login Action ---
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
                set_active_user(username)
                settings_manager.update("account", "username", username)
                settings_manager.update("account", "logged_in", True)
                if profile_callback:
                    profile_callback(username)
                show_message_box(parent_button, "Login", f"Logged in successfully as: {username}", QMessageBox.Information)
            else:
                show_message_box(parent_button, "Login Failed", "Authentication failed. Try again.", QMessageBox.Warning)
    login_action.triggered.connect(login)

    # --- Logout Action ---
    logout_action = QAction("Logout", account_menu)
    def logout():
        if settings_manager.account.logged_in:
            clear_active_user()
            settings_manager.update("account", "username", "")
            settings_manager.update("account", "logged_in", False)
            if profile_callback:
                profile_callback(None)
            show_message_box(parent_button, "Logout", "You have been logged out.", QMessageBox.Information)
        else:
            show_message_box(parent_button, "Logout", "No user is currently logged in.", QMessageBox.Warning)
    logout_action.triggered.connect(logout)

    # Enable/Disable login/logout buttons based on login state
    login_action.setEnabled(not settings_manager.account.logged_in)
    logout_action.setEnabled(settings_manager.account.logged_in)

    # Add actions to account menu
    account_menu.addAction(signup_action)
    account_menu.addAction(login_action)
    account_menu.addAction(logout_action)

    # Add submenus to main settings menu
    main_menu.addMenu(volume_menu)
    main_menu.addMenu(account_menu)

    # Show the menu at button's bottom-right position
    main_menu.exec_(parent_button.mapToGlobal(parent_button.rect().bottomRight()))
