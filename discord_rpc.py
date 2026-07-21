import time
import threading
from typing import Optional

try:
    from pypresence import Presence
    HAS_RPC = True
except ImportError:
    HAS_RPC = False

CLIENT_ID = "1529185031510032414"


class DiscordRPC:
    def __init__(self):
        self._rpc: Optional[Presence] = None
        self._connected = False
        self._start_time = int(time.time())
        self._lock = threading.Lock()

    @property
    def is_connected(self) -> bool:
        return self._connected

    def connect(self):
        if not HAS_RPC:
            return

        def _connect():
            try:
                self._rpc = Presence(CLIENT_ID)
                self._rpc.connect()
                self._connected = True
                self.set_idle()
            except Exception:
                self._connected = False

        threading.Thread(target=_connect, daemon=True).start()

    def disconnect(self):
        with self._lock:
            if self._rpc and self._connected:
                try:
                    self._rpc.close()
                except Exception:
                    pass
                self._connected = False

    def _update(self, details: str, state: str, large_image: str = "mccommand",
                large_text: str = "ANONLauncher",
                small_image: str = "", small_text: str = ""):
        if not self._connected or not self._rpc:
            return
        with self._lock:
            try:
                kwargs = {
                    "details": details,
                    "state": state,
                    "start": self._start_time,
                    "large_image": large_image,
                    "large_text": large_text,
                }
                if small_image:
                    kwargs["small_image"] = small_image
                    kwargs["small_text"] = small_text
                self._rpc.update(**kwargs)
            except Exception:
                self._connected = False

    def set_idle(self):
        self._update(
            details="Idle",
            state="Browsing launcher",
            large_image="mccommand",
            large_text="ANONLauncher",
        )

    def set_browsing_versions(self):
        self._update(
            details="Browsing Versions",
            state="Looking for a version to install",
            large_image="mccommand",
            large_text="Version Manager",
        )

    def set_installing_version(self, version: str):
        self._update(
            details=f"Installing {version}",
            state="Downloading game files...",
            large_image="mccommand",
            large_text="Downloading",
        )

    def set_playing(self, version: str, username: str):
        self._update(
            details=f"Playing Minecraft {version}",
            state=f"As {username}",
            large_image="mccommand",
            large_text="In Game",
        )

    def set_launching(self, version: str):
        self._update(
            details=f"Launching Minecraft {version}",
            state="Starting game...",
            large_image="mccommand",
            large_text="Launching",
        )

    def set_accounts(self):
        self._update(
            details="Managing Accounts",
            state="Configuring login",
            large_image="mccommand",
            large_text="Accounts",
        )

    def set_settings(self):
        self._update(
            details="Settings",
            state="Configuring launcher",
            large_image="mccommand",
            large_text="Settings",
        )

    def set_console(self):
        self._update(
            details="Console",
            state="Viewing game logs",
            large_image="mccommand",
            large_text="Console",
        )
