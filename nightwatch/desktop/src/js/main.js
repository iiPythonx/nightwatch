// Copyright (c) 2024 iiPython

// Setup main store (for future use)
const store = new Store(".nightwatch.dat");

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

// HTML prevention in marked
const preprocess = (markdown) => {
    return markdown
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
};
marked.use({ hooks: { preprocess } });

// Setup emoji
const emoji = new EmojiConvertor();
emoji.replace_mode = "css";
emoji.use_sheet = true;
emoji.img_set = "twitter";
emoji.img_sets.twitter.sheet = "./emoji/sheet_twitter_64.png";

// Handle message processing
const appWindow = window.__TAURI__.window.appWindow;
const container = $("#messages-container");
async function process_message(message) {
    if (!message.user) message.user = { name: "Nightwatch", color: "gray" };

    // Render the message (Markdown + Santization + Emoji)
    message.text = DOMPurify.sanitize(emoji.replace_colons(marked.parse(message.text)), { USE_PROFILES: { html: true } });

    let latest;
    if (window._last_user !== message.user.name) {
        latest = $(`<li class = "list-group-item"><span style = "color: ${message.user.color}">${message.user.name}</span>: ${message.text}</li>`);
        container.append(latest);
        window._last_user = message.user.name;
    } else {
        latest = $(message.text);
        container.children().last().append(latest);
    }
    latest.find("a").attr("target", "_blank");

    // Handle autoscrolling
    const newMessageHeight = latest[0].offsetHeight + parseInt(getComputedStyle(latest[0]).marginBottom);
    const scrollOffset = container[0].scrollTop + container[0].offsetHeight;
    if (container[0].scrollHeight - newMessageHeight <= scrollOffset + 10) container[0].scrollTop = container[0].scrollHeight;

    // Handle notifications
    if (!(await appWindow.isFocused())) notificationAudio.play();
}

// Handle identification step
$("#connect-form").on("submit", (e) => {
    e.preventDefault();

    // Establish connection
    const nw = new NightwatchServer($("#connect-address").val());
    const ws_error = (m) => { nw.close(); notifier.alert(m); delete nw; delete window.nightwatch; }  // Cleanest way I could come up with

    // Handle callbacks
    nw.on_error = () => ws_error("Connection to server failed.");
    nw.connected = () => {
        nw.identify($("#connect-username").val(), window._usercolor || "#fefefe", (d) => {
            if (d.type == "error") ws_error(d.data.text);
            $("#server-name").text(d.data.name);
            ui.switch("messages");
        });
    };

    // Handle messages
    nw.on_message = (message) => {
        message = message.data;
        if ((message.user && message.user.name !== nw.user?.name) || !message.user) process_message(message);
    };

    // Expose our API
    window.nightwatch = nw;
});
$("#btn-logout").on("click", () => {
    window.nightwatch.close();
    delete window.nightwatch;
    ui.switch("connect");
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
