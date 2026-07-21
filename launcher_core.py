import os
import subprocess
import threading
from typing import Callable, Optional

import minecraft_launcher_lib as mll
from minecraft_launcher_lib.utils import get_minecraft_directory
from minecraft_launcher_lib.install import install_minecraft_version

from anonlauncher.auth import Account
from anonlauncher.settings import Settings


class GameLauncher:
    def __init__(self):
        self._process: Optional[subprocess.Popen] = None
        self._thread: Optional[threading.Thread] = None
        self._is_running = False

    @property
    def is_running(self) -> bool:
        return self._is_running

    def get_minecraft_dir(self, game_directory: str = "") -> str:
        if game_directory:
            return game_directory
        return get_minecraft_directory()

    def launch(
        self,
        account: Account,
        settings: Settings,
        version_id: str,
        on_output: Optional[Callable[[str], None]] = None,
        on_exit: Optional[Callable[[int], None]] = None,
    ):
        if self._is_running:
            return

        game_dir = settings.get_game_directory()
        mc_dir = self.get_minecraft_dir(game_dir)

        install_minecraft_version(version_id, game_dir)

        options = {
            "username": account.username,
            "uuid": account.uuid,
            "token": account.token,
            "jvmArguments": [],
            "launcherName": "ANONLauncher",
            "launcherVersion": "1.0.0",
        }

        if settings.min_memory:
            options["jvmArguments"].append(f"-Xms{settings.min_memory}M")
        if settings.max_memory:
            options["jvmArguments"].append(f"-Xmx{settings.max_memory}M")
        if settings.extra_jvm_args:
            options["jvmArguments"].extend(settings.extra_jvm_args.split())

        game_args = []
        if settings.width:
            game_args.append(f"--width {settings.width}")
        if settings.height:
            game_args.append(f"--height {settings.height}")
        if settings.fullscreen:
            game_args.append("--fullscreen")
        if settings.extra_game_args:
            game_args.extend(settings.extra_game_args.split())

        if game_args:
            options["customArgs"] = game_args

        command = mll.command.get_minecraft_command(
            version_id, mc_dir, options
        )

        def _run():
            self._is_running = True
            try:
                self._process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    cwd=mc_dir,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                )
                for line in self._process.stdout:
                    if on_output:
                        on_output(line.strip())
                self._process.wait()
                exit_code = self._process.returncode
                if on_exit:
                    on_exit(exit_code)
            except Exception as e:
                if on_output:
                    on_output(f"[ANONLauncher] Error: {e}")
                if on_exit:
                    on_exit(-1)
            finally:
                self._is_running = False
                self._process = None

        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()

    def kill(self):
        if self._process:
            self._process.terminate()
            self._is_running = False
