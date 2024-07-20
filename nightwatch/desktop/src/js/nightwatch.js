// Copyright (c) 2024 iiPython

// Modules
const { Store } = window.__TAURI__.store;

// Initialization
const notifier = new AWN({});

// Authentication
class Nightwatch {
    constructor() {
        this.store = new Store("nightwatch.dat");
        this.auth_server = "auth.iipython.dev";
    }

    // Handle local authentication
    async authenticate() {
        this.token = await this.store.get("token");
        if (!this.token) return;

        // Fetch user data
        this.user = (await this.request("profile", { token: this.token })).data;
        this.user.id = `${this.user.username}:${this.user.domain}`;
    }
    async set_token(token) {
        this.token = token;
        await this.store.set("token", token);
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

// Handle initial frame loading
(async () => {
    await nightwatch.authenticate();
    load_frame(nightwatch.token ? "welcome" : "auth/login");
})();
