const { app, BrowserWindow, ipcMain, globalShortcut, shell } = require('electron');
const path = require('path');
const os = require('os');

const fs = require('fs');

function logToDisk(msg) {
    const timestamp = new Date().toISOString();
    const formattedMsg = `[${timestamp}] ${msg}\n`;
    console.log(msg);
    try {
        const logPath = path.join(app.getPath('userData'), 'steamworks_debug.log');
        fs.appendFileSync(logPath, formattedMsg);
    } catch (e) {
        try {
            fs.appendFileSync(path.join(__dirname, 'steamworks_debug.log'), formattedMsg);
        } catch (e2) {
            try {
                fs.appendFileSync(path.join(os.tmpdir(), 'theredpearlsofborneo_debug.log'), formattedMsg);
            } catch (e3) { }
        }
    }
}

// Ensure the log file starts clean or at least we know it's a new run
logToDisk("--- NEW APPLICATION LAUNCH ---");

process.on('uncaughtException', (err) => {
    logToDisk(`UNCAUGHT EXCEPTION: ${err.message}\n${err.stack}`);
});

process.on('unhandledRejection', (reason, promise) => {
    logToDisk(`UNHANDLED REJECTION: ${reason}`);
});

// Steam Deck & Linux often require sandbox disabled for AppImage or flatpak-like environments
app.commandLine.appendSwitch('no-sandbox');
app.commandLine.appendSwitch('disable-seccomp-filter-sandbox');

let steamClient;
try {
    const steamworks = require('steamworks.js');
    steamworks.electronEnableSteamOverlay();
    let appIdStr = null;
    let appId = null;

    try {
        appIdStr = fs.readFileSync(path.join(__dirname, 'steam_appid.txt'), 'utf8').trim();
        appId = parseInt(appIdStr, 10);
    } catch (e) {

    }

    if (appId && !isNaN(appId)) {
        steamClient = steamworks.init(appId);
        logToDisk(`Steamworks initialized successfully with local App ID: ${appId}`);
    } else {
        steamClient = steamworks.init();
        logToDisk("Steamworks initialized successfully via Steam Client Environment");
    }
} catch (error) {
    logToDisk(`Failed to initialize Steamworks: ${error.message || error}`);
}

function createWindow() {
    const isSteamDeck = process.env.SteamDeck === '1' || !!process.env.STEAM_COMPAT_DATA_PATH;
    if (isSteamDeck) {
        logToDisk("Steam Deck / SteamOS environment detected. Forcing Fullscreen.");
    }

    const mainWindow = new BrowserWindow({
        width: 1280,
        height: 720,
        fullscreen: isSteamDeck,
        fullscreenable: true,
        resizable: true,
        maximizable: true,
        autoHideMenuBar: true,
        titleBarStyle: process.platform === 'darwin' ? 'hidden' : 'default',
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
            additionalArguments: isSteamDeck ? ['--steam-deck'] : []
        }
    });

    if (process.platform !== 'darwin') {
        mainWindow.setMenuBarVisibility(false);
        mainWindow.setMenu(null);
    }
    
    if (!isSteamDeck && process.platform !== 'darwin') {
        mainWindow.maximize();
    }

    mainWindow.webContents.setWindowOpenHandler(({ url }) => {
        shell.openExternal(url);
        return { action: 'deny' };
    });

    // Handle F11 fullscreen locally without stealing global OS shortcuts
    mainWindow.webContents.on('before-input-event', (event, input) => {
        if (input.key === 'F11' && input.type === 'keyDown') {
            mainWindow.setFullScreen(!mainWindow.isFullScreen());
            event.preventDefault();
        }
    });

    const isDev = !app.isPackaged;
    if (isDev) {
        mainWindow.loadURL('http://localhost:5173');
        mainWindow.webContents.openDevTools();
    } else {
        mainWindow.loadFile(path.join(__dirname, 'dist', 'index.html'));
    }
}

app.whenReady().then(() => {
    createWindow();

    app.on('activate', function () {
        if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
});

app.on('window-all-closed', function () {
    globalShortcut.unregisterAll();
    if (process.platform !== 'darwin') app.quit();
});

ipcMain.handle('open-external', (event, url) => {
    shell.openExternal(url);
});

if (steamClient) {
    ipcMain.handle('steam-unlock-achievement', (event, achId) => {
        try {
            logToDisk(`Attempting to unlock achievement: ${achId}`);
            steamClient.achievement.activate(achId);
            logToDisk(`Successfully called activate for achievement: ${achId}`);
            return true;
        } catch (e) {
            logToDisk(`Failed to unlock achievement ${achId}. Error: ${e.message}`);
            return false;
        }
    });

    ipcMain.handle('steam-cloud-write', (event, filename, data) => {
        try {
            steamClient.cloud.writeFile(filename, data);
            return true;
        } catch (e) {
            console.error('Failed to write to steam cloud', e);
            return false;
        }
    });

    ipcMain.handle('steam-cloud-read', (event, filename) => {
        try {
            if (steamClient.cloud.fileExists(filename)) {
                return steamClient.cloud.readFile(filename);
            }
            return null;
        } catch (e) {
            console.error('Failed to read from steam cloud', e);
            return null;
        }
    });

    ipcMain.handle('steam-clear-achievement', (event, achId) => {
        try {
            logToDisk(`Attempting to CLEAR achievement: ${achId}`);
            steamClient.achievement.clear(achId);
            return true;
        } catch (e) {
            logToDisk(`Failed to clear achievement ${achId}. Error: ${e.message}`);
            return false;
        }
    });

    ipcMain.handle('steam-reset-all-stats', (event) => {
        try {
            logToDisk(`Attempting to RESET ALL STATS AND ACHIEVEMENTS`);
            steamClient.stats.resetAll(true); // true = include achievements
            return true;
        } catch (e) {
            logToDisk(`Failed to reset all stats. Error: ${e.message}`);
            return false;
        }
    });
}
