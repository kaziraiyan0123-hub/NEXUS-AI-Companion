"""
NEXUS Interactive Desktop Spawner
Spawns NEXUS directly onto the active interactive Windows desktop (WinSta0\\default).
"""
import subprocess
import sys
import os

def launch():
    nexus_dir = os.path.dirname(os.path.abspath(__file__))
    python_exe = os.path.join(nexus_dir, ".venv", "Scripts", "python.exe")
    main_py = os.path.join(nexus_dir, "main.py")

    si = subprocess.STARTUPINFO()
    si.lpDesktop = r"WinSta0\default"

    DETACHED_PROCESS = 0x00000008
    CREATE_NEW_PROCESS_GROUP = 0x00000200

    proc = subprocess.Popen(
        [python_exe, main_py],
        startupinfo=si,
        cwd=nexus_dir,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP,
        close_fds=True
    )
    print(f"Spawned NEXUS on WinSta0\\default with PID: {proc.pid}")

if __name__ == "__main__":
    launch()
