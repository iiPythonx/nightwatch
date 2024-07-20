// Handle initial frame loading
async function main_login() {
    main.innerHTML = `
        <div class = "d-flex gap-2 align-items-center" id = "loading">
            <div class = "spinner-border spinner-border-sm" role = "status"></div>
            <span>Logging in</span>
        </div>
    `;
    await nightwatch.authenticate();
    document.getElementById("loading").remove();
    
    // Check for failure
    if (nightwatch._error) return load_frame(`errors/${nightwatch._error.type}`);
    load_frame(nightwatch.token ? "welcome" : "auth/login");
}
main_login();

// Handle adding servers
document.getElementById("add-server").addEventListener("click", () => {
    if (+localStorage.getItem("acknowledged")) return load_frame_as_modal("server/add");
    load_frame_as_modal("server/notice");
});
