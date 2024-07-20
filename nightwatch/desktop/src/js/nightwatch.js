// Copyright (c) 2024 iiPython

// Initialization
const notifier = new AWN({});

// Authentication
class Nightwatch {
    constructor() {
        this.servers = JSON.parse(localStorage.getItem("servers") || "[]");
        this.auth_server = "auth.iipython.dev";
    }

    // Handle servers
    async add_server(server) {
        try {
            const resp = await fetch(`https://${server.replace("/gateway", "/info")}`);
            const info = { url: server, ...(await resp.json()) };
            if (resp.status !== 200 || !info.version) return { type: "fail", message: "Nightwatch didn't respond." };
            if (this.servers.map(x => x.url).includes(server)) return { type: "fail", message: "Server already added." };

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
        return await (await fetch(`https://${this.auth_server}/api/${endpoint}`, {
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
}

const nightwatch = new Nightwatch();
