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
        - Install the Tauri CLI: `cargo install tauri-cli`.
        - Launch via `cargo tauri dev` inside the `nightwatch/desktop/` folder.

# Server Installation

Running a Nightwatch server can be a bit trickier then running the client, but follow along:

- You'll need either [CPython 3.10 or above](https://python.org/downloads), or **preferably**, [PyPy 3.10](https://www.pypy.org/download.html). 
- Install the following dependencies: `pypy3 -m pip install ujson socketify`.
- Launch the server via `pypy3 -m nightwatch.server`.

For more possible ways to run the server, please refer to the [socketify.py documentation](https://docs.socketify.dev/cli.html).

# Configuration

Configuration is available at:
- ***nix systems**: ~/.config/nightwatch/config.json
- **Windows**: %AppData%\Local\Nightwatch\config.json

The Nightwatch client currently allows you to store custom colors and username data there.  
The server currently only uses it for `server.name`. Although that is prone to change.
