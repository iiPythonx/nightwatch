// Copyright (c) 2024 iiPython

// Settings
class NightwatchSettingsHandler {
    constructor() {
        this.button = document.querySelector("ul.nav button");
        this.icon = this.button.querySelector("li");
    }
    set_image_url(url) {
        if (!url) {
            this.button.removeAttribute("data-bs-toggle");
            this.icon.innerHTML = `
                <svg style = "width: 24px; height: 24px;" xmlns="http://www.w3.org/2000/svg" fill="currentColor" class="bi bi-gear" viewBox="0 0 16 16">
                    <path d="M8 4.754a3.246 3.246 0 1 0 0 6.492 3.246 3.246 0 0 0 0-6.492M5.754 8a2.246 2.246 0 1 1 4.492 0 2.246 2.246 0 0 1-4.492 0"/>
                    <path d="M9.796 1.343c-.527-1.79-3.065-1.79-3.592 0l-.094.319a.873.873 0 0 1-1.255.52l-.292-.16c-1.64-.892-3.433.902-2.54 2.541l.159.292a.873.873 0 0 1-.52 1.255l-.319.094c-1.79.527-1.79 3.065 0 3.592l.319.094a.873.873 0 0 1 .52 1.255l-.16.292c-.892 1.64.901 3.434 2.541 2.54l.292-.159a.873.873 0 0 1 1.255.52l.094.319c.527 1.79 3.065 1.79 3.592 0l.094-.319a.873.873 0 0 1 1.255-.52l.292.16c1.64.893 3.434-.902 2.54-2.541l-.159-.292a.873.873 0 0 1 .52-1.255l.319-.094c1.79-.527 1.79-3.065 0-3.592l-.319-.094a.873.873 0 0 1-.52-1.255l.16-.292c.893-1.64-.902-3.433-2.541-2.54l-.292.159a.873.873 0 0 1-1.255-.52zm-2.633.283c.246-.835 1.428-.835 1.674 0l.094.319a1.873 1.873 0 0 0 2.693 1.115l.291-.16c.764-.415 1.6.42 1.184 1.185l-.159.292a1.873 1.873 0 0 0 1.116 2.692l.318.094c.835.246.835 1.428 0 1.674l-.319.094a1.873 1.873 0 0 0-1.115 2.693l.16.291c.415.764-.42 1.6-1.185 1.184l-.291-.159a1.873 1.873 0 0 0-2.693 1.116l-.094.318c-.246.835-1.428.835-1.674 0l-.094-.319a1.873 1.873 0 0 0-2.692-1.115l-.292.16c-.764.415-1.6-.42-1.184-1.185l.159-.291A1.873 1.873 0 0 0 1.945 8.93l-.319-.094c-.835-.246-.835-1.428 0-1.674l.319-.094A1.873 1.873 0 0 0 3.06 4.377l-.16-.292c-.415-.764.42-1.6 1.185-1.184l.292.159a1.873 1.873 0 0 0 2.692-1.115z"/>
                </svg>
            `;
            return this.button.parentElement.querySelector("ul").classList.remove("show");
        }
        this.icon.innerHTML = `<img src = "${url}">`;
        this.button.setAttribute("data-bs-toggle", "dropdown");
    }
}

// Servers
class NightwatchServerHandler {
    constructor() {
        this.servers = JSON.parse(localStorage.getItem("servers") || "[]");
    }
    async add_server(server) {
        if (this.servers.map(x => x.url).includes(server)) return { type: "fail", message: "Server already added." };
        try {
            const resp = await fetch(`https://${server.replace("/gateway", "/info")}`);
            const info = { url: server, ...(await resp.json()) };
            if (resp.status !== 200 || !info.version) return { type: "fail", message: "Nightwatch didn't respond." };

            // Add server to list
            this.servers.push(info);
            localStorage.setItem("servers", JSON.stringify(this.servers));

            if (this.on_server_added) this.on_server_added(info);
            return { type: "success", data: info }
        } catch (error) { return { type: "fail", message: "Failed to connect to server." }; }
    }
    remove_server(server) {
        this.servers = this.servers.filter(x => x.url !== server);
        localStorage.setItem("servers", JSON.stringify(this.servers));
        if (this.on_server_removed) this.on_server_removed({ url: server });
    }
}

// Authentication
class NightwatchAuthHandler {
    constructor() {
        this.server = "auth.iipython.dev";
    }

    // Handle local authentication
    async authenticate() {
        this.token = this.token || localStorage.getItem("token");
        if (!this.token) return;

        // Fetch user data
        try {
            const response = await this.request("profile", { token: this.token })
            if (response.code === 200)  {
                this.user = response.data;
                this.user.id = `${this.user.username}:${this.user.domain}`;
                this.generate_pfp_url();
                return;
            }
            this._error = { type: "login", message: response.data };
        } catch (error) { this._error = { type: "network", message: error.toString() }; }
    }
    async set_token(token) {
        this.token = token;
        localStorage.setItem("token", token);
    }

    // Handle authentication
    async request(endpoint, payload) {
        return await (await fetch(`https://${this.server}/api/${endpoint}`, {
            method: "POST",
            body: JSON.stringify(payload),
            headers: { "Content-Type": "application/json" }
        })).json();
    }
    async login(username, password) {
        const response = await this.request("login", { username, password })
        if (response.code === 200) this.set_token(response.data);
        return response;
    }
    async signup(username, password) {
        const response = await this.request("signup", { username, password })
        if (response.code === 200) this.set_token(response.data);
        return response;
    }
    async authorize(server) {
        return await this.request("authorize", { token: this.token, server })
    }

    // Profile pictures
    generate_pfp_url() {
        this.picture = `https://${this.server}/cdn/pfp/${this.user.username}?t=${new Date().getTime()}`;
        return this.picture;
    }

    // Logging out
    logout() {
        delete this.user;
        this.token = null;
        localStorage.removeItem("token");
        document.getElementById("serverList").innerHTML = "";
        nightwatch.frame.load("auth/login");
        nightwatch.settings.set_image_url();
    }
}

// Exporting
const nightwatch = {
    auth: new NightwatchAuthHandler(),
    conn: new NightwatchServerHandler(),
    settings: new NightwatchSettingsHandler(),
};
