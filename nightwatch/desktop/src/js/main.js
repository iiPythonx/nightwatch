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

// Handle message processing
const container = $("#messages-container");
function process_message(message) {
    if (!message.user) message.user = { name: "Nightwatch", color: "gray" };
    container.append($(`<li class = "list-group-item"><span style = "color: ${message.user.color}">${message.user.name}</span>: ${message.text}</li>`))
}

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
    nw.on_message((message) => {
        if ((message.user && message.user.name !== nw.user?.name) || !message.user) process_message(message);
    });

    // Expose our API
    window.nightwatch = nw;
});

// Handle message sending
const messageInput = $("#message-input");
messageInput.on("keyup", (e) => {
    if (e.keyCode !== 13) return;

    // Input sanity check
    const value = messageInput.val();
    if (!value.trim().length || value.length >= 300) return;

    // Show our message immediately (qol)
    process_message({
        user: window.nightwatch.user,
        text: value
    });

    // Send the actual message to the server
    window.nightwatch.message(value);
    messageInput.val("");
});
