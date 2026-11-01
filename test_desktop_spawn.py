import subprocess
import sys

si = subprocess.STARTUPINFO()
si.lpDesktop = r"WinSta0\default"

cmd = [
    sys.executable,
    "-c",
    "from PySide6.QtWidgets import QApplication, QLabel\n"
    "import time\n"
    "app = QApplication([])\n"
    "lbl = QLabel('HELLO FROM REAL DESKTOP')\n"
    "lbl.resize(300, 100)\n"
    "lbl.show()\n"
    "print('GUI shown on WinSta0 default!')\n"
    "app.processEvents()\n"
]

proc = subprocess.Popen(cmd, startupinfo=si, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
out, err = proc.communicate(timeout=5)
print("STDOUT:", out)
print("STDERR:", err)
