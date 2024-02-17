// Copyright (c) 2024 iiPython

// Main server class
class NightwatchServer {
    constructor(address) {
        address = address.split(":");

        this.host = address[0];
        this.port = address[1] ? Number(address[1]) : 443;

        // Connect socket
        this._callbacks = {};
        this.connect();
    }

    connect() {
        this.socket = new WebSocket(`${this.port == 443 ? 'wss' : 'ws'}://${this.host}:${this.port}/gateway`);
        this.socket.addEventListener("message", (d) => {
            console.warn(d.data);
        });
    }
    
    send_payload(type, data, callback) {
        if (!this.socket) throw new Error("Current Nightwatch websocket is not connected!");
        if (callback) {
            let callback_id = nanoid();
            data.callback = callback_id;
            this._callbacks[callback_id] = callback;
        }
        this.socket.send(JSON.stringify({ type: type, ...data }));
    }

    // Main events
    identify(username) {
        this.send_payload("identify", { name: username, color: "#fefefe" });
    }
}
