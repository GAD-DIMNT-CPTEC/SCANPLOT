const { app, BrowserWindow } = require('electron');

function createWindow() {
    let win = new BrowserWindow({ width: 1280, height: 960, autoHideMenuBar: true });
    win.loadURL('http://localhost:5006'); // Altere a URL se necessário
}

app.whenReady().then(createWindow);

