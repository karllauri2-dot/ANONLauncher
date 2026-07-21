import json
import os
import uuid
import time
import threading
import webbrowser
from dataclasses import dataclass, asdict
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Optional
from urllib.parse import urlparse, parse_qs

import minecraft_launcher_lib.microsoft_account as ms

ACCOUNTS_FILE = os.path.join(os.path.dirname(__file__), "..", "accounts.json")

AZURE_APP_CLIENT_ID = "747bf062-ab9c-4690-842d-a77d18d4cf82"
REDIRECT_PORT = 8080
REDIRECT_URI = f"http://localhost:{REDIRECT_PORT}/token"


@dataclass
class Account:
    username: str
    uuid: str
    token: str
    account_type: str = "offline"
    client_token: str = ""
    last_selected: bool = False
    refresh_token: str = ""

    @property
    def display_name(self) -> str:
        return self.username


class _AuthCallbackHandler(BaseHTTPRequestHandler):
    auth_code: Optional[str] = None

    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)
        if "code" in query:
            _AuthCallbackHandler.auth_code = query["code"][0]
            self.send_response(301)
            self.send_header("Location", "about:blank")
            self.end_headers()
        elif "error" in query:
            _AuthCallbackHandler.auth_code = None
            self.send_response(301)
            self.send_header("Location", "about:blank")
            self.end_headers()
        else:
            self.send_response(301)
            self.send_header("Location", "about:blank")
            self.end_headers()

    def log_message(self, format, *args):
        pass


class MicrosoftLoginFlow:
    def __init__(self):
        self._server: Optional[HTTPServer] = None
        self._server_thread: Optional[threading.Thread] = None
        self._login_thread: Optional[threading.Thread] = None

    def start_login(self, on_success=None, on_error=None):
        _AuthCallbackHandler.auth_code = None

        try:
            self._server = HTTPServer(("localhost", REDIRECT_PORT), _AuthCallbackHandler)
        except OSError as e:
            if on_error:
                on_error(f"Port {REDIRECT_PORT} is in use. Close other programs using it and try again.")
            return

        self._server_thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._server_thread.start()

        login_url, state, code_verifier = ms.get_secure_login_data(
            AZURE_APP_CLIENT_ID, REDIRECT_URI
        )
        webbrowser.open(login_url)

        def _wait_for_code():
            timeout = 300
            elapsed = 0
            while _AuthCallbackHandler.auth_code is None and elapsed < timeout:
                time.sleep(1)
                elapsed += 1

            try:
                self._server.shutdown()
            except Exception:
                pass

            if _AuthCallbackHandler.auth_code is None:
                if on_error:
                    on_error("Login timed out or was cancelled.")
                return

            auth_code = _AuthCallbackHandler.auth_code
            _AuthCallbackHandler.auth_code = None

            try:
                parsed_code = ms.parse_auth_code_url(
                    f"http://localhost:{REDIRECT_PORT}/token?code={auth_code}&state={state}",
                    state,
                )
                result = ms.complete_login(
                    AZURE_APP_CLIENT_ID,
                    None,
                    REDIRECT_URI,
                    parsed_code,
                    code_verifier,
                )
                if on_success:
                    on_success(result)
            except AssertionError:
                if on_error:
                    on_error("State mismatch - please try again.")
            except Exception as e:
                if on_error:
                    on_error(str(e))

        self._login_thread = threading.Thread(target=_wait_for_code, daemon=True)
        self._login_thread.start()


class AuthManager:
    def __init__(self):
        self.accounts: list[Account] = []
        self._load()

    def _accounts_path(self) -> str:
        return os.path.normpath(ACCOUNTS_FILE)

    def _load(self):
        path = self._accounts_path()
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                for acc_data in data.get("accounts", []):
                    if "refresh_token" not in acc_data:
                        acc_data["refresh_token"] = ""
                    self.accounts.append(Account(**acc_data))
            except (json.JSONDecodeError, TypeError):
                self.accounts = []

    def _save(self):
        path = self._accounts_path()
        data = {"accounts": [asdict(a) for a in self.accounts]}
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def add_offline_account(self, username: str) -> Account:
        user_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, username))
        token = str(uuid.uuid4())
        client_token = str(uuid.uuid4())

        account = Account(
            username=username,
            uuid=user_uuid,
            token=token,
            account_type="offline",
            client_token=client_token,
        )

        self.accounts.append(account)
        self._save()
        return account

    def add_microsoft_account(self, login_data: dict) -> Account:
        account = Account(
            username=login_data["name"],
            uuid=login_data["id"],
            token=login_data["access_token"],
            account_type="microsoft",
            refresh_token=login_data.get("refresh_token", ""),
        )

        existing = next(
            (a for a in self.accounts if a.uuid == account.uuid), None
        )
        if existing:
            existing.token = account.token
            existing.refresh_token = account.refresh_token
            existing.username = account.username
            self._save()
            return existing

        self.accounts.append(account)
        self._save()
        return account

    def refresh_microsoft_account(self, account: Account) -> Optional[Account]:
        if account.account_type != "microsoft" or not account.refresh_token:
            return None

        try:
            result = ms.complete_refresh(
                AZURE_APP_CLIENT_ID,
                account.refresh_token,
            )
            account.token = result["access_token"]
            account.refresh_token = result.get("refresh_token", account.refresh_token)
            account.username = result["name"]
            account.uuid = result["id"]
            self._save()
            return account
        except Exception:
            return None

    def remove_account(self, username: str):
        self.accounts = [a for a in self.accounts if a.username != username]
        self._save()

    def get_selected_account(self) -> Optional[Account]:
        for acc in self.accounts:
            if acc.last_selected:
                return acc
        if self.accounts:
            return self.accounts[0]
        return None

    def select_account(self, username: str):
        for acc in self.accounts:
            acc.last_selected = acc.username == username
        self._save()
