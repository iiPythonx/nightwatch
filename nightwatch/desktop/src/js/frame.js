// Copyright (c) 2024 iiPython

// Handle loading frames
class NightwatchFrameHandler {
    constructor() {
        this.main = document.querySelector("main");
    }
    async load(id) {
        this.main.innerHTML = "";
        this.main.append(document.createRange().createContextualFragment(
            await (await fetch(`/frames/${id}.html`)).text()
        ));
    }
    async load_as_modal(id) {
        this.open_modal(document.createRange().createContextualFragment(
            await (await fetch(`/frames/${id}.html`)).text()
        ));
    }

    // Handle modals
    close_modal() {
        const active_modal = document.getElementById("nw-modal");
        if (active_modal) active_modal.remove();
    }
    open_modal(dom) {
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

    // Handle tooltips
    remove_tooltip() {
        const tooltip = document.getElementById("tooltip");
        if (tooltip) tooltip.remove();
        if (this.popper) {
            this.popper.destroy();
            delete this.popper;
        }
    }
    create_tooltip(element, text) {
        this.remove_tooltip();
        const tooltip = document.createElement("div");
        tooltip.innerHTML = `<p>${text}</p>`;
        tooltip.id = "tooltip";
        tooltip.classList.add("nw-tooltip")
        document.body.appendChild(tooltip);
        this.popper = Popper.createPopper(element, tooltip, {
            modifiers: [
                {
                    name: "offset",
                    options: { offset: [ 0, 8 ] }
                }
            ],
            placement: "bottom"
        });
    }
}

// Exporting
nightwatch.frame = new NightwatchFrameHandler();
