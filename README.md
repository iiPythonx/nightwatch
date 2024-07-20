<h1 align = "center">Nightwatch</h1>
<div align = "center">

![Python](https://img.shields.io/badge/Python-%3E=%203.10-4b8bbe?style=for-the-badge&logo=python&logoColor=white)
![Rust](https://img.shields.io/badge/Rust-%3E=%201.60-221f1e?style=for-the-badge&logo=rust&logoColor=white)

The chatting application to end all chatting applications. 

</div>

# Installation

As an end-user, you have multiple clients to pick from when it comes to accessing Nightwatch.  
Here are two of the standard clients for you to choose from:
- Terminal Client ([based on urwid](https://urwid.org/index.html))
    - Installation is as simple as `pip install nightwatch-chat`.
    - The client can be started by running `nightwatch` in your terminal.

- Full Desktop App ([based on tauri](https://tauri.app/))
    - Download the latest release for your system from [here](https://github.com/iiPythonx/nightwatch/releases/latest).
    - Alternatively, run it manually:
        - Follow the instructions from [Tauri prerequisites](https://tauri.app/v1/guides/getting-started/prerequisites) (including installing [Rust](https://rust-lang.org)).
        - Install the Tauri CLI with `cd nightwatch/desktop && bun i`.
        - Launch via `bun run tauri dev`.

# Server Installation

Running a Nightwatch server is a piece of cake:
```sh
# Make a virtual environment for Nightwatch
uv venv
source .venv/bin/activate

# Install the server and its dependencies
uv pip install nightwatch-chat[serve]

# Edit the configuration
mkdir -p ~/.config/nightwatch
nano ~/.config/nightwatch/config.json

# Launch the server
python3 -m nightwatch.server
```

# Configuration

Configuration is available at:
- ***nix systems**: ~/.config/nightwatch/config.json
- **Windows**: %AppData%\Local\Nightwatch\config.json

An example config with all available options is as follows:
```jsonc
{
    "server": {
        "connections": {
            "redis": {
                "address": "redis.example.com",

                // Password is optional
                "password": "somerandompassword"
            },
            "mongodb": "mongodb://user:pass@mongodb.example.com"
        },

        // Icon URL for your server
        // To be replaced by a self hosted icon in the future
        "icon_url": "https://example.com/images/icon.png",

        // If your auth server is auth.example.com and you want
        // IDs to use example.com instead, specify that here.
        // example.com/.well-known/nightwatch will need to return
        // auth.example.com for this to be accepted by servers.
        "domain": "example.com"
    },
    "client": {
        "username": "iiPythonx",
        "user_color": "#126bf1",
        "servers": [
            "localhost:8000",
            "nightwatch.example.com"
        ]
    }
}
```
