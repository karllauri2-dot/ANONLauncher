import threading
from typing import Callable, Optional

import minecraft_launcher_lib as mll
from minecraft_launcher_lib.install import install_minecraft_version


class DownloadManager:
    def __init__(self):
        self._cancel_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._is_downloading = False
        self._progress: dict = {}

    @property
    def is_downloading(self) -> bool:
        return self._is_downloading

    def get_installed_versions(self, game_dir: str) -> list[dict]:
        return mll.utils.get_installed_versions(game_dir)

    def get_available_versions(self) -> list[dict]:
        try:
            versions = mll.utils.get_version_list()
            return versions
        except Exception:
            return []

    def install_version(
        self,
        version_id: str,
        game_dir: str,
        callback: Optional[Callable] = None,
    ):
        if self._is_downloading:
            return

        self._cancel_event.clear()
        self._is_downloading = True
        self._progress = {}

        def _progress_callback(status: dict):
            self._progress = status
            if callback:
                callback(status)

        def _install():
            try:
                install_minecraft_version(
                    version_id,
                    game_dir,
                    callback=_progress_callback,
                    cancelled=self._cancel_event.is_set,
                )
            except Exception as e:
                self._progress = {"error": str(e)}
                if callback:
                    callback(self._progress)
            finally:
                self._is_downloading = False

        self._thread = threading.Thread(target=_install, daemon=True)
        self._thread.start()

    def cancel_download(self):
        self._cancel_event.set()
        self._is_downloading = False

    def get_progress(self) -> dict:
        return self._progress.copy()
