import sys
import os
import tkinter as tk

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from anonlauncher.gui import ANONLauncherApp


def main():
    root = tk.Tk()

    root.tk.call("tk", "scaling", 1.25)

    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    app = ANONLauncherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
