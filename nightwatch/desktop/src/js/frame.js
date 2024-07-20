// Copyright (c) 2024 iiPython

// Handle loading frames
const main = document.querySelector("main");
async function load_frame(identifier) {
    main.innerHTML = "";
    main.append(document.createRange().createContextualFragment(
        await (await fetch(`/frames/${identifier}.html`)).text()
    ));
}

async function load_frame_as_modal(identifier) {
    open_modal(document.createRange().createContextualFragment(
        await (await fetch(`/frames/${identifier}.html`)).text()
    ));
}

// Handle modals
function close_modal() {
    const active_modal = document.getElementById("nw-modal");
    if (active_modal) active_modal.remove();
}
function open_modal(dom) {
    let active_modal = document.getElementById("nw-modal");
    if (!active_modal) {
        active_modal = document.createElement("div");
        parent = document.createElement("div");
        parent.id = "nw-modal";
        parent.appendChild(active_modal);
        document.body.append(parent);

        // Handle click to close
        active_modal.addEventListener("click", (e) => e.stopPropagation());
        parent.addEventListener("click", () => parent.remove());
    };
    active_modal.innerHTML = "";
    active_modal.append(dom);
}
