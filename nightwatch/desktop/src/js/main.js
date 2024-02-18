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

// Handle notifications
const notifier = new AWN({ icons: { enabled: false } });
const notificationAudio = new Audio("../audio/notification.mp3");

// Handle message processing
const appWindow = window.__TAURI__.window.appWindow;
const container = $("#messages-container");
async function process_message(message) {
    if (!message.user) message.user = { name: "Nightwatch", color: "gray" };
    const latest = $(`<li class = "list-group-item"><span style = "color: ${message.user.color}">${message.user.name}</span>: ${message.text}</li>`)[0];
    container.append(latest);

    // Handle autoscrolling
    const newMessageHeight = latest.offsetHeight + parseInt(getComputedStyle(latest).marginBottom);
    const scrollOffset = container[0].scrollTop + container[0].offsetHeight;
    if (container[0].scrollHeight - newMessageHeight <= scrollOffset + 10) {
        container[0].scrollTop = container[0].scrollHeight;
    }

    // Handle notifications
    if (!(await appWindow.isFocused())) notificationAudio.play();
}

// Handle identification step
$("#connect-form").on("submit", (e) => {
    e.preventDefault();

    // Establish connection
    const nw = new NightwatchServer($("#connect-address").val());
    nw.connected(() => {
        nw.identify($("#connect-username").val(), window._usercolor || "#fefefe", (d) => {
            if (d.type == "error") return notifier.alert(d.data.text);
            $("#server-name").text(d.data.name);
            ui.switch("messages");
        });
    });

    // Handle messages
    nw.on_message((message) => {
        message = message.data;
        if ((message.user && message.user.name !== nw.user?.name) || !message.user) process_message(message);
    });

    // Expose our API
    window.nightwatch = nw;
});

// Handle message sending
const messageInput = document.getElementById("message-input");
messageInput.addEventListener("keypress", (e) => {
    if (e.key == "Enter") {
        const value = e.target.value;
        if (!value.trim().length || value.length >= 300) return;
        process_message({ user: window.nightwatch.user, text: value });
        window.nightwatch.message(value);
        messageInput.value = "";
    }
});

// Handle color selection
const pickr = Pickr.create({
    el: ".color-picker", theme: "nano",
    components: { preview: true, hue: true, opacity: true }
});
pickr.on("change", () => { pickr.applyColor(); });
pickr.on("save", (c) => { window._usercolor = c ? c.toHEXA().toString() : null; });
