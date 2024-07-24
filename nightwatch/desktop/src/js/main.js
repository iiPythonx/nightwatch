(() => {

    // Imports
    const { auth, frame, settings } = nightwatch;

    // Handle initial frame loading
    window.main_login = async () => {
        frame.main.innerHTML = `
            <div class = "d-flex gap-2 align-items-center" id = "loading">
                <div class = "spinner-border spinner-border-sm" role = "status"></div>
                <span>Logging in</span>
            </div>
        `;
        await auth.authenticate();
        document.getElementById("loading").remove();
        
        // Check for failure
        if (auth._error) return frame.load(`errors/${auth._error.type}`);
        frame.load(auth.token ? "welcome" : "auth/login");
    }
    main_login();

    // Handle settings icon
    settings.set_image_url();
    settings.button.addEventListener("click", () => {
        if (settings.button.getAttribute("data-bs-toggle")) return;
        frame.load_as_modal("settings");
    });
})();
