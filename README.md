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

- Browser App
    - Available in the `nightwatch/web` folder.
    - Alternatively, access it at [nightwatch.iipython.dev](https://nightwatch.iipython.dev).

# Server Installation

Running a Nightwatch server can be a bit trickier then running the client, but follow along:

```sh
git clone https://github.com/iiPythonx/nightwatch && cd nightwatch
git checkout release
uv venv
uv pip install -e .
uvicorn nightwatch.rics:app --host 0.0.0.0
```

An example NGINX configuration:

```conf
server {

    # SSL
    listen              443 ssl;
    ssl_certificate     /etc/ssl/nightwatch.pem;
    ssl_certificate_key /etc/ssl/nightwatch.key;

    # Setup location
    server_name nightwatch.iipython.dev;
    location /api {
        proxy_pass http://192.168.0.1:8000;
        proxy_http_version 1.1;
    }
    location /api/ws {
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection upgrade;
        proxy_pass http://192.168.0.1:8000/api/ws;
        proxy_http_version 1.1;
    }
}
```

# Configuration

Configuration is available at:
- ***nix systems**: ~/.config/nightwatch
- **Windows**: %LocalAppData%\Nightwatch

Client (terminal) configuration is available at `client.json`, while the server configuration is stored in `rics.json`.  
The Nightwatch client uses the JSON for username, coloring, and more. Check the `/config` command for more information. 
The backend chat server uses the config file for the server name, although more is sure to come.
