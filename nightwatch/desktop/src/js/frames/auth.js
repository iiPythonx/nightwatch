(() => {
    const form = document.querySelector("form"), button = document.querySelector("button[type = submit]");
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        button.innerHTML = `<div class = "spinner-border spinner-border-sm" role = "status"></div>`;

        // Handle authentication
        const response = await nightwatch[form.getAttribute("data-nightwatch-action")](
            document.getElementById("usernameInput").value,
            document.getElementById("passwordInput").value
        )
        if (response.code !== 200) {
            button.innerText = "Continue";
            return notifier.alert(response.data);
        }

        await nightwatch.authenticate();
        if (nightwatch._error) return load_frame(`errors/${nightwatch._error.type}`);
        load_frame("welcome");
    });
    document.getElementById("authServer").innerText = nightwatch.auth_server;
})();
