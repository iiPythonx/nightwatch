// Copyright (c) 2024 iiPython

// General UI handler
class UIStateManager {
    constructor() {
        this.last_state = "#state-connect";
    }

    switch(state) {
        state = `#state-${state}`;
        $(this.last_state).css("display", "none");

        $(state).css("display", "block");
        this.last_state = state;
    }
}

const ui = new UIStateManager();

// Handle identification step
$("#connect-form").on("submit", (e) => {
    e.preventDefault();

    // Establish connection
    const nw = new NightwatchServer($("#connect-address").val());
    nw.connected(() => {
        nw.identify($("#connect-username").val(), "#fefefe", (d) => {
            if (d.text) return console.error(d.text);
            ui.switch("messages");
        });
    });

    // Handle messages
    const container = $("#messages-container");
    nw.on_message((message) => {
        if (!message.user) message.user = { name: "Nightwatch", color: "gray" };
        container.append($(`<li class = "list-group-item"><span style = "color: ${message.user.color}">${message.user.name}</span>: ${message.text}</li>`))
    });

    // Expose our API
    window.nightwatch = nw;
});

// Handle message sending
const messageInput = $("#message-input");
messageInput.on("keyup", (e) => {
    if (e.keyCode !== 13) return;
    const value = messageInput.val();
    if (!value.trim().length) return;
    window.nightwatch.message(value);
    messageInput.val("");
});
