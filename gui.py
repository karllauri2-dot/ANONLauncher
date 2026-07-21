import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
from typing import Optional

from anonlauncher.auth import AuthManager, Account, MicrosoftLoginFlow
from anonlauncher.settings import SettingsManager, Settings
from anonlauncher.downloader import DownloadManager
from anonlauncher.launcher_core import GameLauncher
from anonlauncher.discord_rpc import DiscordRPC

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

COLORS = {
    "bg_dark": "#000000",
    "bg_medium": "#0a0a0a",
    "bg_light": "#003300",
    "accent": "#00ff41",
    "accent_hover": "#39ff14",
    "text_primary": "#00ff41",
    "text_secondary": "#00cc33",
    "text_muted": "#006622",
    "success": "#00ff41",
    "warning": "#ccff00",
    "error": "#ff0000",
    "input_bg": "#001a00",
    "input_border": "#003300",
    "sidebar_bg": "#000a00",
    "card_bg": "#001200",
    "border": "#003300",
    "glow": "#00ff41",
    "bright_green": "#39ff14",
    "dark_green": "#004400",
}

FONTS = {
    "title": ("Consolas", 28, "bold"),
    "heading": ("Consolas", 16, "bold"),
    "subheading": ("Consolas", 12, "bold"),
    "body": ("Consolas", 10),
    "small": ("Consolas", 9),
    "mono": ("Consolas", 10),
    "logo": ("Consolas", 36, "bold"),
}


class ANONLauncherApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("ANONLauncher")
        self.root.geometry("960x640")
        self.root.minsize(960, 640)
        self.root.configure(bg=COLORS["bg_dark"])
        self.root.resizable(True, True)

        try:
            self.root.iconbitmap(default="")
        except Exception:
            pass

        self.auth = AuthManager()
        self.settings_mgr = SettingsManager()
        self.downloader = DownloadManager()
        self.launcher = GameLauncher()
        self.rpc = DiscordRPC()
        self.rpc.connect()

        self.current_frame: Optional[tk.Frame] = None
        self.sidebar_buttons: list[dict] = []

        self._build_ui()
        self._show_page("home")

    def _on_closing(self):
        self.rpc.disconnect()
        self.root.destroy()

    def _build_ui(self):
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        self.sidebar = tk.Frame(self.root, bg=COLORS["sidebar_bg"], width=220)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        logo_frame = tk.Frame(self.sidebar, bg=COLORS["sidebar_bg"])
        logo_frame.pack(fill="x", pady=(20, 30), padx=15)

        tk.Label(
            logo_frame,
            text="ANON",
            font=("Consolas", 20, "bold"),
            fg=COLORS["accent"],
            bg=COLORS["sidebar_bg"],
        ).pack(side="left")
        tk.Label(
            logo_frame,
            text="Launcher",
            font=("Consolas", 20, "bold"),
            fg=COLORS["bright_green"],
            bg=COLORS["sidebar_bg"],
        ).pack(side="left")

        separator = tk.Frame(self.sidebar, bg=COLORS["border"], height=1)
        separator.pack(fill="x", padx=15, pady=(0, 10))

        nav_items = [
            ("home", "Home"),
            ("versions", "Versions"),
            ("accounts", "Accounts"),
            ("settings", "Settings"),
            ("logs", "Console"),
        ]

        for page_id, label in nav_items:
            btn = self._create_nav_button(page_id, label)
            btn.pack(fill="x", padx=10, pady=2)

        spacer = tk.Frame(self.sidebar, bg=COLORS["sidebar_bg"])
        spacer.pack(fill="both", expand=True)

        version_label = tk.Label(
            self.sidebar,
            text="ANONLauncher v1.0.0",
            font=FONTS["small"],
            fg=COLORS["text_muted"],
            bg=COLORS["sidebar_bg"],
        )
        version_label.pack(side="bottom", pady=10)

        self.content_area = tk.Frame(self.root, bg=COLORS["bg_dark"])
        self.content_area.grid(row=0, column=1, sticky="nsew")
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=1)

    def _create_nav_button(self, page_id: str, label: str) -> tk.Frame:
        btn_frame = tk.Frame(
            self.sidebar, bg=COLORS["sidebar_bg"], cursor="hand2"
        )

        indicator = tk.Frame(btn_frame, bg=COLORS["sidebar_bg"], width=3)
        indicator.pack(side="left", fill="y")

        text_label = tk.Label(
            btn_frame,
            text=f"  {label}",
            font=FONTS["body"],
            fg=COLORS["text_secondary"],
            bg=COLORS["sidebar_bg"],
            anchor="w",
        )
        text_label.pack(fill="x", padx=5, pady=8)

        def on_enter(e):
            if btn_frame._page_id != self._current_page:
                btn_frame.configure(bg=COLORS["bg_medium"])
                text_label.configure(bg=COLORS["bg_medium"])

        def on_leave(e):
            if btn_frame._page_id != self._current_page:
                btn_frame.configure(bg=COLORS["sidebar_bg"])
                text_label.configure(bg=COLORS["sidebar_bg"])

        def on_click(e):
            self._show_page(page_id)

        for widget in [btn_frame, text_label]:
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_click)

        btn_frame._page_id = page_id
        btn_frame._indicator = indicator
        btn_frame._text_label = text_label
        self.sidebar_buttons.append({"frame": btn_frame, "id": page_id})

        return btn_frame

    def _update_nav(self, active_page: str):
        self._current_page = active_page
        for btn_info in self.sidebar_buttons:
            frame = btn_info["frame"]
            page = btn_info["id"]
            indicator = frame._indicator
            label = frame._text_label

            if page == active_page:
                frame.configure(bg=COLORS["bg_light"])
                label.configure(bg=COLORS["bg_light"], fg=COLORS["text_primary"])
                indicator.configure(bg=COLORS["accent"])
            else:
                frame.configure(bg=COLORS["sidebar_bg"])
                label.configure(bg=COLORS["sidebar_bg"], fg=COLORS["text_secondary"])
                indicator.configure(bg=COLORS["sidebar_bg"])

    def _show_page(self, page_id: str):
        if self.current_frame:
            self.current_frame.destroy()

        self._update_nav(page_id)

        rpc_map = {
            "home": self.rpc.set_idle,
            "versions": self.rpc.set_browsing_versions,
            "accounts": self.rpc.set_accounts,
            "settings": self.rpc.set_settings,
            "logs": self.rpc.set_console,
        }
        rpc_fn = rpc_map.get(page_id)
        if rpc_fn:
            rpc_fn()

        pages = {
            "home": self._build_home_page,
            "versions": self._build_versions_page,
            "accounts": self._build_accounts_page,
            "settings": self._build_settings_page,
            "logs": self._build_logs_page,
        }

        builder = pages.get(page_id)
        if builder:
            self.current_frame = builder()
            self.current_frame.grid(row=0, column=0, sticky="nsew")

    def _make_card(self, parent, **kwargs) -> tk.Frame:
        card = tk.Frame(parent, bg=COLORS["card_bg"], relief="flat", **kwargs)
        return card

    def _make_button(self, parent, text, command=None, style="primary", **kwargs) -> tk.Button:
        styles = {
            "primary": (COLORS["accent"], COLORS["text_primary"], COLORS["accent_hover"]),
            "secondary": (COLORS["bg_light"], COLORS["text_primary"], COLORS["bg_medium"]),
            "danger": (COLORS["error"], COLORS["text_primary"], "#c0392b"),
            "success": (COLORS["success"], COLORS["text_primary"], "#27ae60"),
        }
        bg, fg, hover_bg = styles.get(style, styles["primary"])

        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=hover_bg,
            activeforeground=fg,
            font=FONTS["subheading"],
            relief="flat",
            cursor="hand2",
            bd=0,
            padx=20,
            pady=8,
            **kwargs,
        )

        def on_enter(e):
            btn.configure(bg=hover_bg)

        def on_leave(e):
            btn.configure(bg=bg)

        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    def _make_entry(self, parent, **kwargs) -> tk.Entry:
        entry = tk.Entry(
            parent,
            bg=COLORS["input_bg"],
            fg=COLORS["text_primary"],
            insertbackground=COLORS["text_primary"],
            font=FONTS["body"],
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"],
            **kwargs,
        )
        return entry

    def _make_label(self, parent, text, style="body", **kwargs) -> tk.Label:
        fg = kwargs.pop("fg", COLORS["text_primary"])
        label = tk.Label(
            parent,
            text=text,
            font=FONTS.get(style, FONTS["body"]),
            fg=fg,
            bg=kwargs.pop("bg", COLORS["card_bg"]),
            **kwargs,
        )
        return label

    def _start_matrix_rain(self, canvas: tk.Canvas):
        import random
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$%^&*()_+-=[]{}|;':\",./<>?アイウエオカキクケコサシスセソタチツテトナニヌネノ"
        drops = []
        canvas_width = 900
        canvas_height = 150
        char_width = 14
        num_columns = canvas_width // char_width

        for i in range(num_columns):
            drops.append({
                "x": i * char_width,
                "y": random.randint(-canvas_height, 0),
                "speed": random.randint(3, 8),
                "chars": [random.choice(chars) for _ in range(20)],
                "length": random.randint(5, 15),
            })

        def animate():
            canvas.delete("all")
            canvas.create_rectangle(0, 0, canvas_width, canvas_height, fill="#000000", outline="")
            for drop in drops:
                y = drop["y"]
                for j in range(drop["length"]):
                    char_y = y - j * 16
                    if 0 <= char_y <= canvas_height:
                        char = random.choice(chars) if random.random() < 0.05 else drop["chars"][j % len(drop["chars"])]
                        if j == 0:
                            color = "#ffffff"
                        elif j < 3:
                            color = "#39ff14"
                        else:
                            color = "#00ff41" if j < 8 else "#008f11"
                        canvas.create_text(
                            drop["x"], char_y,
                            text=char,
                            fill=color,
                            font=("Consolas", 11),
                            anchor="nw",
                        )
                drop["y"] += drop["speed"]
                if drop["y"] - drop["length"] * 16 > canvas_height:
                    drop["y"] = random.randint(-100, -10)
                    drop["speed"] = random.randint(3, 8)
                    drop["length"] = random.randint(5, 15)
            self._rain_after_id = canvas.after(80, animate)

        self._rain_after_id = canvas.after(0, animate)

    # ─── PAGES ───────────────────────────────────────────────────────

    def _build_home_page(self) -> tk.Frame:
        frame = tk.Frame(self.content_area, bg=COLORS["bg_dark"])

        # Matrix rain canvas
        rain_canvas = tk.Canvas(
            frame, bg="#000000", highlightthickness=0, height=150
        )
        rain_canvas.pack(fill="x")
        self._start_matrix_rain(rain_canvas)

        top_section = tk.Frame(frame, bg=COLORS["bg_dark"])
        top_section.pack(fill="x", padx=40, pady=(20, 20))

        tk.Label(
            top_section,
            text="> ANONLauncher initialized_",
            font=FONTS["title"],
            fg=COLORS["accent"],
            bg=COLORS["bg_dark"],
        ).pack(anchor="w")

        tk.Label(
            top_section,
            text="> Select an account and start playing Minecraft...",
            font=FONTS["body"],
            fg=COLORS["text_muted"],
            bg=COLORS["bg_dark"],
        ).pack(anchor="w", pady=(5, 0))

        center = tk.Frame(frame, bg=COLORS["bg_dark"])
        center.pack(expand=True, fill="both", padx=40)

        status_card = self._make_card(center)
        status_card.pack(fill="x", pady=(0, 20))
        status_inner = tk.Frame(status_card, bg=COLORS["card_bg"])
        status_inner.pack(fill="x", padx=20, pady=20)

        account = self.auth.get_selected_account()
        if account:
            acc_type = "Microsoft" if account.account_type == "microsoft" else "Offline"
            status_text = f"{account.username} ({acc_type})"
            status_color = COLORS["success"]
        else:
            status_text = "No account selected"
            status_color = COLORS["warning"]

        tk.Label(
            status_inner,
            text="Account",
            font=FONTS["small"],
            fg=COLORS["text_muted"],
            bg=COLORS["card_bg"],
        ).pack(anchor="w")
        tk.Label(
            status_inner,
            text=status_text,
            font=FONTS["subheading"],
            fg=status_color,
            bg=COLORS["card_bg"],
        ).pack(anchor="w", pady=(2, 10))

        installed = self.downloader.get_installed_versions(
            self.settings_mgr.settings.get_game_directory()
        )
        version_text = f"{len(installed)} version(s) installed"
        tk.Label(
            status_inner,
            text="Versions",
            font=FONTS["small"],
            fg=COLORS["text_muted"],
            bg=COLORS["card_bg"],
        ).pack(anchor="w")
        tk.Label(
            status_inner,
            text=version_text,
            font=FONTS["subheading"],
            fg=COLORS["text_primary"],
            bg=COLORS["card_bg"],
        ).pack(anchor="w", pady=(2, 10))

        launch_card = self._make_card(center)
        launch_card.pack(fill="x", pady=(0, 20))
        launch_inner = tk.Frame(launch_card, bg=COLORS["card_bg"])
        launch_inner.pack(fill="x", padx=20, pady=20)

        self._make_label(
            launch_inner, "Quick Launch", style="subheading"
        ).pack(anchor="w")

        version_frame = tk.Frame(launch_inner, bg=COLORS["card_bg"])
        version_frame.pack(fill="x", pady=(10, 0))

        self._make_label(version_frame, "Version:").pack(side="left")

        self.home_version_var = tk.StringVar(value="latest")
        self.home_version_combo = ttk.Combobox(
            version_frame,
            textvariable=self.home_version_var,
            state="readonly",
            font=FONTS["body"],
            width=30,
        )
        self.home_version_combo.pack(side="left", padx=(10, 0))

        installed_versions = self.downloader.get_installed_versions(
            self.settings_mgr.settings.get_game_directory()
        )
        version_list = ["latest"] + [
            v.get("id", "") for v in installed_versions
        ]
        self.home_version_combo["values"] = version_list
        if installed_versions:
            self.home_version_combo.current(0)

        btn_frame = tk.Frame(launch_inner, bg=COLORS["card_bg"])
        btn_frame.pack(fill="x", pady=(20, 0))

        if not account:
            self.launch_btn = self._make_button(
                btn_frame,
                "No Account - Go to Accounts",
                command=lambda: self._show_page("accounts"),
                style="secondary",
            )
        elif self.downloader.is_downloading:
            self.launch_btn = self._make_button(
                btn_frame,
                "Installing...",
                style="secondary",
            )
        elif not installed_versions:
            self.launch_btn = self._make_button(
                btn_frame,
                "Install & Play",
                command=self._launch_with_install,
                style="success",
            )
        else:
            self.launch_btn = self._make_button(
                btn_frame,
                "Launch",
                command=self._launch_game,
                style="success",
            )
        self.launch_btn.pack(side="left")

        self.launch_status_label = self._make_label(
            btn_frame, "", fg=COLORS["text_secondary"], style="small"
        )
        self.launch_status_label.pack(side="left", padx=15)

        info_card = self._make_card(center)
        info_card.pack(fill="x")
        info_inner = tk.Frame(info_card, bg=COLORS["card_bg"])
        info_inner.pack(fill="x", padx=20, pady=15)

        features = [
            "> Download & install Minecraft versions",
            "> Microsoft account authentication",
            "> Offline account support",
            "> Customizable Java & memory settings",
            "> Clean and lightweight launcher",
        ]
        for feat in features:
            row = tk.Frame(info_inner, bg=COLORS["card_bg"])
            row.pack(fill="x", pady=2)
            tk.Label(
                row,
                text="*",
                font=FONTS["body"],
                fg=COLORS["accent"],
                bg=COLORS["card_bg"],
            ).pack(side="left")
            tk.Label(
                row,
                text=f"  {feat}",
                font=FONTS["small"],
                fg=COLORS["text_secondary"],
                bg=COLORS["card_bg"],
            ).pack(side="left")

        return frame

    def _build_versions_page(self) -> tk.Frame:
        frame = tk.Frame(self.content_area, bg=COLORS["bg_dark"])

        header = tk.Frame(frame, bg=COLORS["bg_dark"])
        header.pack(fill="x", padx=40, pady=(30, 10))

        tk.Label(
            header,
            text="> Versions_",
            font=FONTS["title"],
            fg=COLORS["accent"],
            bg=COLORS["bg_dark"],
        ).pack(side="left")

        self._make_button(
            header, "Refresh", command=self._refresh_versions, style="secondary"
        ).pack(side="right")

        tabs = tk.Frame(frame, bg=COLORS["bg_dark"])
        tabs.pack(fill="x", padx=40, pady=(5, 10))

        self.versions_tab_var = tk.StringVar(value="installed")

        self.installed_tab_btn = tk.Label(
            tabs,
            text="Installed",
            font=FONTS["subheading"],
            fg=COLORS["accent"],
            bg=COLORS["bg_dark"],
            cursor="hand2",
        )
        self.installed_tab_btn.pack(side="left", padx=(0, 20))
        self.installed_tab_btn.bind(
            "<Button-1>", lambda e: self._switch_version_tab("installed")
        )

        self.available_tab_btn = tk.Label(
            tabs,
            text="Available",
            font=FONTS["subheading"],
            fg=COLORS["text_muted"],
            bg=COLORS["bg_dark"],
            cursor="hand2",
        )
        self.available_tab_btn.pack(side="left", padx=(0, 20))
        self.available_tab_btn.bind(
            "<Button-1>", lambda e: self._switch_version_tab("available")
        )

        list_frame_outer = tk.Frame(frame, bg=COLORS["bg_dark"])
        list_frame_outer.pack(fill="both", expand=True, padx=40, pady=(0, 20))

        self.versions_list_frame = tk.Frame(
            list_frame_outer, bg=COLORS["bg_dark"]
        )
        self.versions_list_frame.pack(fill="both", expand=True)

        self.progress_frame = tk.Frame(frame, bg=COLORS["bg_dark"])

        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode="determinate",
        )

        self.progress_label = tk.Label(
            self.progress_frame,
            text="",
            font=FONTS["small"],
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_dark"],
        )

        self._load_installed_versions()
        return frame

    def _switch_version_tab(self, tab: str):
        self.versions_tab_var.set(tab)
        if tab == "installed":
            self.installed_tab_btn.configure(fg=COLORS["accent"])
            self.available_tab_btn.configure(fg=COLORS["text_muted"])
            self._load_installed_versions()
        else:
            self.installed_tab_btn.configure(fg=COLORS["text_muted"])
            self.available_tab_btn.configure(fg=COLORS["accent"])
            self._load_available_versions()

    def _load_installed_versions(self):
        for w in self.versions_list_frame.winfo_children():
            w.destroy()

        game_dir = self.settings_mgr.settings.get_game_directory()
        installed = self.downloader.get_installed_versions(game_dir)

        if not installed:
            tk.Label(
                self.versions_list_frame,
                text="No versions installed yet.\nGo to Available tab to install one.",
                font=FONTS["body"],
                fg=COLORS["text_muted"],
                bg=COLORS["bg_dark"],
                justify="center",
            ).pack(expand=True)
            return

        canvas = tk.Canvas(
            self.versions_list_frame,
            bg=COLORS["bg_dark"],
            highlightthickness=0,
        )
        scrollbar = ttk.Scrollbar(
            self.versions_list_frame, orient="vertical", command=canvas.yview
        )
        scroll_frame = tk.Frame(canvas, bg=COLORS["bg_dark"])

        scroll_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for v in installed:
            v_id = v.get("id", "unknown")
            card = self._make_card(scroll_frame)
            card.pack(fill="x", padx=5, pady=4)

            inner = tk.Frame(card, bg=COLORS["card_bg"])
            inner.pack(fill="x", padx=15, pady=10)

            tk.Label(
                inner,
                text=v_id,
                font=FONTS["subheading"],
                fg=COLORS["text_primary"],
                bg=COLORS["card_bg"],
            ).pack(side="left")

            tk.Label(
                inner,
                text="Installed",
                font=FONTS["small"],
                fg=COLORS["success"],
                bg=COLORS["card_bg"],
            ).pack(side="right")

    def _load_available_versions(self):
        for w in self.versions_list_frame.winfo_children():
            w.destroy()

        tk.Label(
            self.versions_list_frame,
            text="Loading versions...",
            font=FONTS["body"],
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_dark"],
        ).pack(expand=True)

        def load():
            versions = self.downloader.get_available_versions()
            self.root.after(0, lambda: self._populate_available(versions))

        threading.Thread(target=load, daemon=True).start()

    def _populate_available(self, versions: list):
        for w in self.versions_list_frame.winfo_children():
            w.destroy()

        if not versions:
            tk.Label(
                self.versions_list_frame,
                text="Could not load versions.",
                font=FONTS["body"],
                fg=COLORS["error"],
                bg=COLORS["bg_dark"],
            ).pack(expand=True)
            return

        canvas = tk.Canvas(
            self.versions_list_frame,
            bg=COLORS["bg_dark"],
            highlightthickness=0,
        )
        scrollbar = ttk.Scrollbar(
            self.versions_list_frame, orient="vertical", command=canvas.yview
        )
        scroll_frame = tk.Frame(canvas, bg=COLORS["bg_dark"])

        scroll_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        release_types = {"release": "Release", "snapshot": "Snapshot", "old_beta": "Old Beta", "old_alpha": "Old Alpha"}

        for v in versions[:80]:
            v_id = v.get("id", "")
            v_type = v.get("type", "")
            type_label = release_types.get(v_type, v_type)

            card = self._make_card(scroll_frame)
            card.pack(fill="x", padx=5, pady=4)

            inner = tk.Frame(card, bg=COLORS["card_bg"])
            inner.pack(fill="x", padx=15, pady=10)

            left = tk.Frame(inner, bg=COLORS["card_bg"])
            left.pack(side="left", fill="x", expand=True)

            tk.Label(
                left,
                text=v_id,
                font=FONTS["subheading"],
                fg=COLORS["text_primary"],
                bg=COLORS["card_bg"],
            ).pack(anchor="w")

            type_color = COLORS["accent"] if v_type == "release" else COLORS["warning"]
            tk.Label(
                left,
                text=type_label,
                font=FONTS["small"],
                fg=type_color,
                bg=COLORS["card_bg"],
            ).pack(anchor="w")

            install_btn = self._make_button(
                inner,
                "Install",
                command=lambda vid=v_id: self._install_version(vid),
                style="primary",
            )
            install_btn.pack(side="right")

    def _install_version(self, version_id: str):
        if self.downloader.is_downloading:
            messagebox.showinfo("Busy", "A download is already in progress.")
            return

        self.progress_frame.pack(fill="x", padx=40, pady=(0, 20))
        self.progress_bar.pack(fill="x")
        self.progress_label.pack(anchor="w", pady=(5, 0))
        self.progress_var.set(0)

        self.rpc.set_installing_version(version_id)

        game_dir = self.settings_mgr.settings.get_game_directory()

        def on_progress(status: dict):
            self.root.after(0, lambda: self._update_progress(status))

        self.downloader.install_version(version_id, game_dir, callback=on_progress)
        self._poll_download()

    def _poll_download(self):
        if self.downloader.is_downloading:
            self.root.after(500, self._poll_download)
        else:
            progress = self.downloader.get_progress()
            if "error" in progress:
                self.progress_label.configure(
                    text=f"Error: {progress['error']}",
                    fg=COLORS["error"],
                )
            else:
                self.progress_var.set(100)
                self.progress_label.configure(
                    text="Installation complete!", fg=COLORS["success"]
                )
            self.rpc.set_idle()
            self.root.after(3000, self._clear_progress)

    def _update_progress(self, status: dict):
        if "progress" in status and "total" in status:
            if status["total"] > 0:
                pct = (status["current"] / status["total"]) * 100
                self.progress_var.set(pct)
        if "task" in status:
            self.progress_label.configure(text=status["task"])

    def _clear_progress(self):
        self.progress_frame.pack_forget()
        self._refresh_versions()

    def _refresh_versions(self):
        if self.versions_tab_var.get() == "installed":
            self._load_installed_versions()
        else:
            self._load_available_versions()

    def _build_accounts_page(self) -> tk.Frame:
        frame = tk.Frame(self.content_area, bg=COLORS["bg_dark"])

        header = tk.Frame(frame, bg=COLORS["bg_dark"])
        header.pack(fill="x", padx=40, pady=(30, 20))

        tk.Label(
            header,
            text="> Accounts_",
            font=FONTS["title"],
            fg=COLORS["accent"],
            bg=COLORS["bg_dark"],
        ).pack(side="left")

        content = tk.Frame(frame, bg=COLORS["bg_dark"])
        content.pack(fill="both", expand=True, padx=40)

        add_card = self._make_card(content)
        add_card.pack(fill="x", pady=(0, 20))
        add_inner = tk.Frame(add_card, bg=COLORS["card_bg"])
        add_inner.pack(fill="x", padx=20, pady=20)

        tk.Label(
            add_inner,
            text="Add Microsoft Account",
            font=FONTS["heading"],
            fg=COLORS["text_primary"],
            bg=COLORS["card_bg"],
        ).pack(anchor="w")

        tk.Label(
            add_inner,
            text="Login with your Microsoft account to play on premium servers",
            font=FONTS["small"],
            fg=COLORS["text_muted"],
            bg=COLORS["card_bg"],
        ).pack(anchor="w", pady=(2, 10))

        ms_frame = tk.Frame(add_inner, bg=COLORS["card_bg"])
        ms_frame.pack(fill="x", pady=(0, 5))

        self.ms_login_btn = self._make_button(
            ms_frame,
            "Login with Microsoft",
            command=self._microsoft_login,
            style="primary",
        )
        self.ms_login_btn.pack(side="left")

        self.ms_login_status = self._make_label(
            ms_frame, "", style="small", fg=COLORS["text_muted"]
        )
        self.ms_login_status.pack(side="left", padx=(15, 0))

        sep_frame = tk.Frame(add_inner, bg=COLORS["card_bg"])
        sep_frame.pack(fill="x", pady=(15, 10))

        sep_line = tk.Frame(sep_frame, bg=COLORS["border"], height=1)
        sep_line.pack(fill="x")

        tk.Label(
            sep_frame,
            text="OR",
            font=FONTS["small"],
            fg=COLORS["text_muted"],
            bg=COLORS["card_bg"],
        ).pack(pady=(5, 5))

        offline_label = tk.Label(
            add_inner,
            text="Add Offline Account",
            font=FONTS["subheading"],
            fg=COLORS["text_secondary"],
            bg=COLORS["card_bg"],
        )
        offline_label.pack(anchor="w", pady=(0, 5))

        tk.Label(
            add_inner,
            text="No authentication - for singleplayer / cracked servers only",
            font=FONTS["small"],
            fg=COLORS["text_muted"],
            bg=COLORS["card_bg"],
        ).pack(anchor="w", pady=(0, 10))

        username_frame = tk.Frame(add_inner, bg=COLORS["card_bg"])
        username_frame.pack(fill="x", pady=(0, 10))

        tk.Label(
            username_frame,
            text="Username:",
            font=FONTS["body"],
            fg=COLORS["text_secondary"],
            bg=COLORS["card_bg"],
        ).pack(side="left")

        self.username_entry = self._make_entry(username_frame, width=30)
        self.username_entry.pack(side="left", padx=(10, 0))

        self._make_button(
            username_frame,
            "Add Offline",
            command=self._add_account,
            style="secondary",
        ).pack(side="left", padx=(15, 0))

        accounts_card = self._make_card(content)
        accounts_card.pack(fill="both", expand=True)
        accounts_inner = tk.Frame(accounts_card, bg=COLORS["card_bg"])
        accounts_inner.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(
            accounts_inner,
            text="Your Accounts",
            font=FONTS["heading"],
            fg=COLORS["text_primary"],
            bg=COLORS["card_bg"],
        ).pack(anchor="w", pady=(0, 10))

        self.accounts_list_frame = tk.Frame(
            accounts_inner, bg=COLORS["card_bg"]
        )
        self.accounts_list_frame.pack(fill="both", expand=True)

        self._refresh_accounts_list()
        return frame

    def _microsoft_login(self):
        self.ms_login_btn.configure(state="disabled", text="Logging in...")
        self.ms_login_status.configure(text="Opening browser...", fg=COLORS["warning"])

        login_flow = MicrosoftLoginFlow()

        def on_success(result):
            self.root.after(0, lambda: self._on_ms_login_success(result))

        def on_error(error):
            self.root.after(0, lambda: self._on_ms_login_error(error))

        login_flow.start_login(on_success=on_success, on_error=on_error)

    def _on_ms_login_success(self, result: dict):
        self.auth.add_microsoft_account(result)
        self.ms_login_btn.configure(state="normal", text="Login with Microsoft")
        self.ms_login_status.configure(
            text=f"Logged in as {result['name']}", fg=COLORS["success"]
        )
        self._refresh_accounts_list()

    def _on_ms_login_error(self, error: str):
        self.ms_login_btn.configure(state="normal", text="Login with Microsoft")
        self.ms_login_status.configure(text=f"Error: {error}", fg=COLORS["error"])

    def _add_account(self):
        username = self.username_entry.get().strip()
        if not username:
            messagebox.showwarning("Warning", "Please enter a username.")
            return

        if len(username) < 2:
            messagebox.showwarning("Warning", "Username must be at least 2 characters.")
            return

        for acc in self.auth.accounts:
            if acc.username == username:
                messagebox.showinfo("Info", "This account already exists.")
                return

        self.auth.add_offline_account(username)
        self.username_entry.delete(0, tk.END)
        self._refresh_accounts_list()

    def _refresh_accounts_list(self):
        for w in self.accounts_list_frame.winfo_children():
            w.destroy()

        if not self.auth.accounts:
            tk.Label(
                self.accounts_list_frame,
                text="No accounts added yet.",
                font=FONTS["body"],
                fg=COLORS["text_muted"],
                bg=COLORS["card_bg"],
            ).pack(pady=20)
            return

        for acc in self.auth.accounts:
            card = tk.Frame(
                self.accounts_list_frame,
                bg=COLORS["input_bg"],
                relief="flat",
            )
            card.pack(fill="x", pady=4)

            inner = tk.Frame(card, bg=COLORS["input_bg"])
            inner.pack(fill="x", padx=15, pady=12)

            left = tk.Frame(inner, bg=COLORS["input_bg"])
            left.pack(side="left", fill="x", expand=True)

            selected = acc.last_selected
            name_color = COLORS["accent"] if selected else COLORS["text_primary"]

            name_row = tk.Frame(left, bg=COLORS["input_bg"])
            name_row.pack(anchor="w")

            tk.Label(
                name_row,
                text=acc.username,
                font=FONTS["subheading"],
                fg=name_color,
                bg=COLORS["input_bg"],
            ).pack(side="left")

            if selected:
                tk.Label(
                    name_row,
                    text=" (active)",
                    font=FONTS["small"],
                    fg=COLORS["success"],
                    bg=COLORS["input_bg"],
                ).pack(side="left")

            type_label = "Microsoft" if acc.account_type == "microsoft" else "Offline"
            type_color = COLORS["accent"] if acc.account_type == "microsoft" else COLORS["text_muted"]

            info_text = f"Type: {type_label}"
            if acc.account_type == "offline":
                info_text += f"  |  UUID: {acc.uuid[:8]}..."

            tk.Label(
                left,
                text=info_text,
                font=FONTS["small"],
                fg=type_color,
                bg=COLORS["input_bg"],
            ).pack(anchor="w", pady=(2, 0))

            right = tk.Frame(inner, bg=COLORS["input_bg"])
            right.pack(side="right")

            if not selected:
                self._make_button(
                    right,
                    "Select",
                    command=lambda a=acc: self._select_account(a.username),
                    style="success",
                ).pack(side="left", padx=(0, 5))

            self._make_button(
                right,
                "Remove",
                command=lambda a=acc: self._remove_account(a.username),
                style="danger",
            ).pack(side="left")

    def _select_account(self, username: str):
        self.auth.select_account(username)
        self._refresh_accounts_list()

    def _remove_account(self, username: str):
        if messagebox.askyesno(
            "Confirm", f"Remove account '{username}'?"
        ):
            self.auth.remove_account(username)
            self._refresh_accounts_list()

    def _build_settings_page(self) -> tk.Frame:
        frame = tk.Frame(self.content_area, bg=COLORS["bg_dark"])

        canvas = tk.Canvas(frame, bg=COLORS["bg_dark"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=COLORS["bg_dark"])

        scroll_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfig(canvas_window, width=e.width),
        )
        canvas_window = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Label(
            scroll_frame,
            text="> Settings_",
            font=FONTS["title"],
            fg=COLORS["accent"],
            bg=COLORS["bg_dark"],
        ).pack(anchor="w", padx=40, pady=(30, 20))

        s = self.settings_mgr.settings

        def add_setting_section(parent, title):
            card = tk.Frame(parent, bg=COLORS["card_bg"])
            card.pack(fill="x", padx=40, pady=(0, 15))
            inner = tk.Frame(card, bg=COLORS["card_bg"])
            inner.pack(fill="x", padx=20, pady=15)
            tk.Label(
                inner,
                text=title,
                font=FONTS["heading"],
                fg=COLORS["text_primary"],
                bg=COLORS["card_bg"],
            ).pack(anchor="w", pady=(0, 10))
            return inner

        def add_field(parent, label_text, default_val, field_name, is_dir=False, is_int=False, is_bool=False):
            row = tk.Frame(parent, bg=COLORS["card_bg"])
            row.pack(fill="x", pady=5)

            tk.Label(
                row,
                text=label_text,
                font=FONTS["body"],
                fg=COLORS["text_secondary"],
                bg=COLORS["card_bg"],
                width=20,
                anchor="w",
            ).pack(side="left")

            if is_bool:
                var = tk.BooleanVar(value=bool(default_val))
                check = tk.Checkbutton(
                    row,
                    variable=var,
                    bg=COLORS["card_bg"],
                    fg=COLORS["text_primary"],
                    selectcolor=COLORS["input_bg"],
                    activebackground=COLORS["card_bg"],
                    activeforeground=COLORS["text_primary"],
                )
                check.pack(side="left")
                return var

            entry = self._make_entry(row, width=40)
            entry.insert(0, str(default_val))
            entry.pack(side="left", padx=(0, 10))

            if is_dir:
                def browse():
                    d = filedialog.askdirectory(initialdir=entry.get() or os.path.expanduser("~"))
                    if d:
                        entry.delete(0, tk.END)
                        entry.insert(0, d)

                self._make_button(
                    row, "Browse", command=browse, style="secondary"
                ).pack(side="left")

            return entry

        sec = add_setting_section(scroll_frame, "Java Settings")
        java_path_var = add_field(
            sec, "Java Path:", s.java_path, "java_path", is_dir=True
        )
        extra_jvm_var = add_field(
            sec, "Extra JVM Args:", s.extra_jvm_args, "extra_jvm_args"
        )

        sec = add_setting_section(scroll_frame, "Memory Settings")
        min_mem_var = add_field(
            sec, "Min Memory (MB):", s.min_memory, "min_memory", is_int=True
        )
        max_mem_var = add_field(
            sec, "Max Memory (MB):", s.max_memory, "max_memory", is_int=True
        )

        sec = add_setting_section(scroll_frame, "Game Settings")
        game_dir_var = add_field(
            sec, "Game Directory:", s.get_game_directory(), "game_directory", is_dir=True
        )
        extra_game_var = add_field(
            sec, "Extra Game Args:", s.extra_game_args, "extra_game_args"
        )

        sec = add_setting_section(scroll_frame, "Window Settings")
        width_var = add_field(sec, "Width:", s.width, "width", is_int=True)
        height_var = add_field(sec, "Height:", s.height, "height", is_int=True)
        fullscreen_var = add_field(
            sec, "Fullscreen:", s.fullscreen, "fullscreen", is_bool=True
        )

        def save_settings():
            try:
                updates = {
                    "java_path": java_path_var.get().strip(),
                    "extra_jvm_args": extra_jvm_var.get().strip(),
                    "min_memory": int(min_mem_var.get()),
                    "max_memory": int(max_mem_var.get()),
                    "game_directory": game_dir_var.get().strip(),
                    "extra_game_args": extra_game_var.get().strip(),
                    "width": int(width_var.get()),
                    "height": int(height_var.get()),
                    "fullscreen": fullscreen_var.get(),
                }
                self.settings_mgr.update(**updates)
                messagebox.showinfo("Saved", "Settings saved successfully!")
            except ValueError:
                messagebox.showerror("Error", "Invalid numeric value in settings.")

        btn_row = tk.Frame(scroll_frame, bg=COLORS["bg_dark"])
        btn_row.pack(fill="x", padx=40, pady=(10, 40))

        self._make_button(
            btn_row, "Save Settings", command=save_settings, style="primary"
        ).pack(side="left")

        return frame

    def _build_logs_page(self) -> tk.Frame:
        frame = tk.Frame(self.content_area, bg=COLORS["bg_dark"])

        header = tk.Frame(frame, bg=COLORS["bg_dark"])
        header.pack(fill="x", padx=40, pady=(30, 10))

        tk.Label(
            header,
            text="> Console_",
            font=FONTS["title"],
            fg=COLORS["accent"],
            bg=COLORS["bg_dark"],
        ).pack(side="left")

        self._make_button(
            header, "Clear", command=self._clear_logs, style="secondary"
        ).pack(side="right")

        log_card = tk.Frame(frame, bg=COLORS["bg_dark"])
        log_card.pack(fill="both", expand=True, padx=40, pady=(0, 20))

        self.log_text = tk.Text(
            log_card,
            bg="#000000",
            fg=COLORS["accent"],
            font=("Consolas", 10),
            insertbackground=COLORS["accent"],
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=COLORS["dark_green"],
            highlightcolor=COLORS["accent"],
            wrap="word",
            state="disabled",
        )

        log_scroll = ttk.Scrollbar(log_card, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)

        self.log_text.pack(side="left", fill="both", expand=True)
        log_scroll.pack(side="right", fill="y")

        self.log_text.tag_configure("info", foreground="#00cc33")
        self.log_text.tag_configure("error", foreground="#ff0000")
        self.log_text.tag_configure("success", foreground="#39ff14")
        self.log_text.tag_configure("accent", foreground="#00ff41")

        self._log("ANONLauncher v1.0.0", "accent")
        self._log("System initialized. Awaiting commands...", "info")

        return frame

    def _log(self, message: str, tag: str = "info"):
        if hasattr(self, "log_text"):
            self.log_text.configure(state="normal")
            timestamp = time.strftime("%H:%M:%S")
            self.log_text.insert("end", f"[{timestamp}]> {message}\n", tag)
            self.log_text.see("end")
            self.log_text.configure(state="disabled")

    def _clear_logs(self):
        if hasattr(self, "log_text"):
            self.log_text.configure(state="normal")
            self.log_text.delete("1.0", "end")
            self.log_text.configure(state="disabled")
            self._log("Console cleared.", "info")

    # ─── LAUNCH ──────────────────────────────────────────────────────

    def _launch_with_install(self):
        account = self.auth.get_selected_account()
        if not account:
            messagebox.showwarning("No Account", "Please add and select an account first.")
            return

        version_id = self.home_version_var.get()
        if not version_id or version_id == "latest":
            try:
                import minecraft_launcher_lib as mll
                version_id = mll.utils.get_latest_version()["release"]
            except Exception:
                version_id = "1.21"

        game_dir = self.settings_mgr.settings.get_game_directory()
        self.launch_status_label.configure(
            text="Installing game files...", fg=COLORS["warning"]
        )

        self.rpc.set_installing_version(version_id)

        def on_progress(status: dict):
            if "task" in status:
                self.root.after(
                    0,
                    lambda t=status["task"]: self.launch_status_label.configure(text=t),
                )

        self.downloader.install_version(version_id, game_dir, callback=on_progress)

        def wait_and_launch():
            while self.downloader.is_downloading:
                time.sleep(1)
            self.root.after(0, self._launch_game)

        threading.Thread(target=wait_and_launch, daemon=True).start()

    def _launch_game(self):
        account = self.auth.get_selected_account()
        if not account:
            messagebox.showwarning("No Account", "Please add and select an account first.")
            return

        version_id = self.home_version_var.get()
        if not version_id or version_id == "latest":
            try:
                import minecraft_launcher_lib as mll
                version_id = mll.utils.get_latest_version()["release"]
            except Exception:
                version_id = "1.21"

        self.launch_btn.configure(state="disabled", text="Launching...")
        self.launch_status_label.configure(
            text="Starting Minecraft...", fg=COLORS["warning"]
        )

        self.rpc.set_launching(version_id)
        self._log(f"Launching {version_id} as {account.username}...", "info")

        def on_output(line):
            self.root.after(0, lambda l=line: self._log(l, "info"))

        def on_exit(code):
            self.root.after(0, lambda: self._on_game_exit(code, version_id, account.username))

        self.launcher.launch(
            account,
            self.settings_mgr.settings,
            version_id,
            on_output=on_output,
            on_exit=on_exit,
        )

    def _on_game_exit(self, code: int, version_id: str = "", username: str = ""):
        self.launch_btn.configure(state="normal", text="Launch")
        self.rpc.set_idle()
        if code == 0:
            self.launch_status_label.configure(
                text="Game exited normally.", fg=COLORS["success"]
            )
            self._log("Game exited normally.", "success")
        else:
            self.launch_status_label.configure(
                text=f"Game exited with code {code}", fg=COLORS["error"]
            )
            self._log(f"Game exited with code {code}", "error")
