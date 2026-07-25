<div align="center">

# ANONLauncher

### OPEN BETA — v1.0.0

A Matrix-inspired Minecraft launcher for Windows.

**No bloat. No ads. No tracking. Just launch.**

[Download (Latest)](../../releases/latest) · [Report Bug](../../issues) · [Request Feature](../../issues/new)

![Status](https://img.shields.io/badge/Status-OPEN%20BETA-brightgreen?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-yellow?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-gray?style=for-the-badge)

</div>

---

> **WARNING: This software is in OPEN BETA.** Things will break. Features will change. You've been warned. Bug reports and contributions are welcome — open an [issue](../../issues) or submit a pull request.

## What is this?

ANONLauncher is a lightweight, standalone Minecraft launcher with a Matrix-style aesthetic. It handles everything from downloading game files to launching Minecraft — all wrapped in a dark terminal-themed interface with animated digital rain.

Built with Python and tkinter. Single .exe output. No installation required.

## Features

| Feature | Details |
|---|---|
| **Matrix UI** | Dark terminal theme with animated falling characters, scanline overlay, and glowing green accents |
| **Microsoft Login** | Full OAuth2 + PKCE authentication flow — sign in through your browser, stays logged in via refresh tokens |
| **Offline Mode** | Play on cracked/singleplayer servers with a custom username |
| **Multi-Loader Support** | Browse and install from Vanilla, Fabric, Forge, and Quilt with filter tabs |
| **Version Manager** | Browse and install any Minecraft version — Release, Snapshot, Old Beta, Old Alpha |
| **Token Grabber** | Extract access tokens from running Minecraft processes — copy to clipboard or import directly |
| **Discord Rich Presence** | Shows what you're doing in the launcher to your Discord friends |
| **Full Settings** | Java path, min/max RAM, window resolution, fullscreen, custom JVM & game arguments, configurable Azure Client ID |
| **Console** | Live game output with timestamped logs in a terminal-style viewer |
| **Portable** | Single .exe file — just run it, no install, no dependencies |

## Screenshot

```
┌─────────────────────────────────────────────────┐
│  ╔═══════════════════════════════════════════╗   │
│  ║  ▓▓▓▓▓  MATRIX RAIN ANIMATION  ▓▓▓▓▓     ║   │
│  ╚═══════════════════════════════════════════╝   │
│                                                  │
│  > ANONLauncher initialized_                     │
│  > Select an account and start playing...        │
│                                                  │
│  ┌─ Account ──────────────────────────────┐     │
│  │  Steve (Microsoft)                     │     │
│  │  3 version(s) installed                │     │
│  └────────────────────────────────────────┘     │
│                                                  │
│  ┌─ Quick Launch ─────────────────────────┐     │
│  │  Version: [1.21.4          ▼]          │     │
│  │  [ Launch ]                            │     │
│  └────────────────────────────────────────┘     │
└─────────────────────────────────────────────────┘
```

## Getting Started

### Download (Recommended)

1. Go to **[Releases](../../releases)**
2. Download `ANONLauncher.exe`
3. Run it — that's it

### Build from Source

```bash
git clone https://github.com/karllauri2-dot/ANONLauncher.git
cd ANONLauncher
pip install -r requirements.txt
python main.py
```

To build the .exe yourself:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name ANONLauncher --icon anonlauncher\assets\icon.ico main.py
```

The .exe will be in the `dist/` folder.

## How It Works

1. **Add an account** — Click Accounts, then "Login with Microsoft" or type a username for offline mode
2. **Pick a version** — Go to Versions, browse with filters (ALL / VANILLA / FABRIC / FORGE / QUILT), hit Install
3. **Launch** — Back on Home, select your version and account, click Launch
4. **Customize** — Settings lets you control Java, RAM, resolution, and more

### Microsoft Login Setup

Microsoft login requires an Azure app with Minecraft API permission. You have two options:

1. **Use the default Client ID** — works if the app already has permission
2. **Register your own Azure app:**
   - Go to https://portal.azure.com
   - App registrations > New registration
   - Name: `ANONLauncher`
   - Redirect URI: `http://localhost:8080/token` (Mobile and desktop applications)
   - Copy the Application (client) ID
   - Apply for Minecraft API access: https://aka.ms/MinecraftAccess
   - Paste the Client ID in Settings > Azure Client ID

### Token Grabber

Already playing on another launcher? Grab your access token:

1. Start Minecraft from any launcher
2. Open ANONLauncher > Accounts
3. Click **"Get Token from Running Game"**
4. Token is copied to your clipboard
5. Paste it in the Token field and click Import

## Project Structure

```
ANONLauncher/
├ main.py                    Entry point
├ requirements.txt           Dependencies
├ README.md
└ anonlauncher/
    ├ __init__.py
    ├ auth.py                Microsoft + offline account management
    ├ settings.py            Settings persistence (JSON)
    ├ downloader.py          Version download (Vanilla, Fabric, Forge, Quilt)
    ├ launcher_core.py       Minecraft launch logic
    ├ gui.py                 Matrix-themed tkinter GUI
    ├ discord_rpc.py         Discord Rich Presence
    ├ get_token.py           Extract tokens from running Java processes
    └ assets/
        ├ icon.ico           Windows icon
        ├ icon.png           256x256 icon
        └ icon_512.png       512x512 icon
```

## Requirements

- **OS:** Windows 10 or 11
- **Java:** Java 21+ (for Minecraft 1.20.5+), Java 17+ (for 1.18+), Java 8+ (for older versions)
- **Discord:** Desktop app running (optional — only for Rich Presence)

## Tech Stack

- **Python 3.10+** — core language
- **tkinter** — GUI framework
- **minecraft-launcher-lib** — version management, Fabric, Forge, Quilt installers, and game launching
- **pypresence** — Discord Rich Presence
- **Pillow** — icon generation
- **PyInstaller** — .exe packaging

## Known Issues (Open Beta)

- Microsoft login requires the Azure app to have Minecraft API permission (may take 24-48h for approval)
- Some antivirus software flags PyInstaller executables — this is a false positive
- No auto-update yet — check back for new releases manually
- No skin preview

## Contributing

1. Fork the repo
2. Create a branch (`git checkout -b feature/my-feature`)
3. Commit (`git commit -m "Add my feature"`)
4. Push (`git push origin feature/my-feature`)
5. Open a Pull Request

## License

MIT License — do whatever you want with it.

---

<div align="center">

**ANONLauncher** is not affiliated with Mojang Studios or Microsoft.

Minecraft is a trademark of Mojang Studios.

</div>
