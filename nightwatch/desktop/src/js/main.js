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
});
