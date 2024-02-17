// Copyright (c) 2024 iiPython
// Under the MIT license, see LICENSE.txt for more information

// Modules
const { app, BrowserWindow } = require("electron");

// Main entrypoint
const createWindow = () => {
    const win = new BrowserWindow({
        width: 800,
        height: 600
    });
    win.loadFile("src/index.html");
}

app.whenReady().then(() => {
    createWindow();
    app.on("activate", () => {
        if (BrowserWindow.getAllWindows().length === 0) createWindow();
    })
})

app.on("window-all-closed", () => {
    if (process.platform !== "darwin") app.quit();
})
