"""
NEXUS — An Intelligent AI Desktop Companion
Main application entry point.
"""
import sys
import os
import logging

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Ensure process attaches to interactive user desktop if launched from background sandbox
if sys.platform == "win32":
    import ctypes
    try:
        user32 = ctypes.windll.user32
        h_desk = user32.OpenDesktopW("default", 0, False, 0x01FF)
        if h_desk:
            user32.SetThreadDesktop(h_desk)
    except Exception as e:
        pass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from core.assistant import NexusAssistant
from desktop.tray import create_default_tray_pixmap

def setup_logging():
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    appdata = os.environ.get("APPDATA")
    if appdata:
        log_dir = os.path.join(appdata, "NEXUS")
    else:
        log_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "nexus.log")
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%H:%M:%S",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    def excepthook(exc_type, exc_value, exc_traceback):
        logging.getLogger("NEXUS.CrashHandler").critical(
            "Unhandled exception:", exc_info=(exc_type, exc_value, exc_traceback)
        )
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
    sys.excepthook = excepthook

_app_mutex = None

def check_single_instance():
    """Windows Named Mutex ensuring only one instance of NEXUS runs simultaneously."""
    global _app_mutex
    if sys.platform != "win32":
        return True
    import ctypes
    ERROR_ALREADY_EXISTS = 183
    kernel32 = ctypes.windll.kernel32
    _app_mutex = kernel32.CreateMutexW(None, False, "Global\\NEXUS_AI_Desktop_Companion_Mutex")
    if kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
        return False
    return True

def main():
    setup_logging()
    logger = logging.getLogger("NEXUS.Main")

    if not check_single_instance():
        logger.warning("Another instance of NEXUS is already active on this desktop. Exiting duplicate launcher.")
        print("NEXUS is already running on your desktop.")
        sys.exit(0)

    logger.info("Initializing NEXUS Desktop Companion...")

    # High-DPI support for Windows 11
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("NEXUS")
    app.setApplicationDisplayName("NEXUS — AI Desktop Companion")
    app.setQuitOnLastWindowClosed(False)

    # Application icon
    app_icon = QIcon(create_default_tray_pixmap())
    app.setWindowIcon(app_icon)

    # Initialize assistant coordinator
    assistant = NexusAssistant(app)
    assistant.start()

    logger.info("NEXUS is live on Windows Desktop.")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
