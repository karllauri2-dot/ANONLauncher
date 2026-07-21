# ANONLauncher - OPEN BETA

> **This software is in OPEN BETA.** Expect bugs, missing features, and breaking changes. Feedback and contributions are welcome.

A lightweight, Matrix-themed Minecraft launcher built with Python. Supports Microsoft account login and offline mode.

## Features

- Matrix-themed UI with animated rain effect on the home screen
- Microsoft account authentication (OAuth2 + PKCE)
- Offline/cracked account support
- Download and install any Minecraft version (Release, Snapshot, Old Beta/Alpha)
- Customizable Java path, memory allocation, window size, and JVM/game arguments
- Discord Rich Presence integration
- Console log viewer
- Single-file .exe — no installation required

## Download

Head to the **[Releases](../../releases)** page and download `ANONLauncher.exe`.

Just run it — no Python installation needed.

## Building from source

```
pip install -r requirements.txt
python main.py
```

To build the .exe:

```
pip install pyinstaller
pyinstaller --onefile --windowed --name ANONLauncher --icon anonlauncher\assets\icon.ico main.py
```

## Project structure

```
ANONLauncher/
├── main.py                    # Entry point
├── requirements.txt
├── README.md
└── anonlauncher/
    ├── __init__.py
    ├── auth.py                # Account management (offline + Microsoft)
    ├── settings.py            # Settings persistence
    ├── downloader.py          # Version download/install
    ├── launcher_core.py       # Game launch logic
    ├── gui.py                 # Matrix-themed tkinter GUI
    ├── discord_rpc.py         # Discord Rich Presence
    └── assets/
        ├── icon.ico
        ├── icon.png
        └── icon_512.png
```

## How it works

1. **Accounts** — Add a Microsoft account (opens browser for login) or an offline username
2. **Versions** — Browse available Minecraft versions, install any you want
3. **Launch** — Select a version and account, hit Launch
4. **Settings** — Configure Java, memory, resolution, and extra arguments

## Requirements

- Windows 10/11
- Java installed (Java 21+ for modern Minecraft)
- Discord desktop app (optional, for Rich Presence)

## License

MIT

## Status

**OPEN BETA** — v1.0.0
