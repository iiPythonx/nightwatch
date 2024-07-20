document.querySelector("form").addEventListener("submit", async (e) => {
    e.preventDefault();

    // Handle authentication
    const response = await window.__NWAUTHMETHOD__(
        document.getElementById("usernameInput").value,
        document.getElementById("passwordInput").value
    )
    if (response.code !== 200) return notifier.alert(response.data);
    load_frame("welcome");
});