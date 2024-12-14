// Copyright (c) 2024 iiPython

const CHARSET = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
const PROTOCOL_VERSION = "0.11.2";

export default class ConnectionManager {
    constructor(payload, callbacks) {
        this.callbacks = callbacks;
        const { username, hex, address } = payload;

        // Handle host and port
        let [ host, port ] = address.split(":");
        port = port ? Number(port) : 443;

        this.url = `${host}:${port}`
        this.protocol = port === 443 ? "s" : "";

        // Perform token authentication
        this.#authenticate(username, hex);
    }
    
    async #connect(authorization) {
        this.websocket = new WebSocket(`ws${this.protocol}://${this.url}/api/ws?authorization=${authorization}`);
        this.websocket.addEventListener("open", async () => {
            this.websocket.addEventListener("message", (e) => this.#on_message(e));
            this.callbacks.on_connect();
        });
        this.websocket.addEventListener("close", e => this.callbacks.on_problem({ type: "generic", data: e.reason || "Connection was closed." }));
        this.websocket.addEventListener("error", e => this.callbacks.on_problem({ type: "something", data: e }));
    }

    async #authenticate(username, hex) {
        try {
            const version_response = await fetch(`http${this.protocol}://${this.url}/api/version`);
            if (!version_response.ok) return this.callbacks.on_problem({ type: "unknown-version" });

            const info = (await version_response.json()).data;
            if (PROTOCOL_VERSION.localeCompare(info.version, undefined, { numeric: true, sensitivity: "base" }) === 1) {
                return this.callbacks.on_problem({ type: "outdated-version", data: { version: info.version, supported: PROTOCOL_VERSION } });
            }

        } catch (e) {
            return this.callbacks.on_problem({ type: "unknown-version" });
        }

        const response = await (await fetch(
            `http${this.protocol}://${this.url}/api/join`,
            {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, hex })
            }
        )).json();
        
        // Establish websocket connection
        this.#connect(response.authorization);
    }

    #on_message(event) {
        const { type, data } = JSON.parse(event.data);
        if (data.callback in this.callbacks) {
            this.callbacks[data.callback](data);
            delete this.callbacks[data.callback];
            return;
        };
        switch (type) {
            case "message":
                this.callbacks.on_message(data);
                break

            case "rics-info":
                document.getElementById("server-name").innerText = data.name;
                for (const message of data["message-log"]) this.callbacks.on_message(message);
                for (const user of data["user-list"]) this.callbacks.handle_member("join", user);
                break;

            case "join":
            case "leave":
                this.callbacks.handle_member(type, data.user);
                break;

            case "problem":
                this.callbacks.on_problem({ type: "generic", data: data.message });
                break;
        }
    }

    #generate_callback = () => {
        let result = "";
        for (let i = 0; i < 10; i++) {
            const randomIndex = Math.floor(Math.random() * CHARSET.length);
            result += CHARSET[randomIndex];
        }
        return result;
    };

    async send(payload, is_callback) {
        if (is_callback) {
            if (!payload.data) payload.data = {};
            payload.data.callback = this.#generate_callback();
            this.websocket.send(JSON.stringify(payload));
            return new Promise((resolve) => { this.callbacks[payload.data.callback] = resolve; });
        };
        this.websocket.send(JSON.stringify(payload));
    }
}
