(() => {

    // Importing
    const { auth, frame } = nightwatch;

    // Handle form submission
    const form = document.querySelector("form"), button = document.querySelector("button[type = submit]");
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        button.innerHTML = `<div class = "spinner-border spinner-border-sm" role = "status"></div>`;

        // Handle authentication
        const response = await auth[form.getAttribute("data-nightwatch-action")](
            document.getElementById("usernameInput").value,
            document.getElementById("passwordInput").value
        )
        if (response.code !== 200) {
            button.innerText = "Continue";
            return console.error(response.data);
        }

        await auth.authenticate();
        if (auth._error) return frame.load(`errors/${auth._error.type}`);
        frame.load("welcome");
    });
    document.getElementById("authServer").innerText = auth.server;
})();
