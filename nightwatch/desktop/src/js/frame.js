// Copyright (c) 2024 iiPython

// Handle loading frames
const main = document.querySelector("main");
async function load_frame(identifier) {
    main.innerHTML = "";
    main.append(document.createRange().createContextualFragment(
        await (await fetch(`/frames/${identifier}.html`)).text()
    ));
}
