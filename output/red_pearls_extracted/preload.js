const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('Steamworks', {
    unlockAchievement: (achId) => ipcRenderer.invoke('steam-unlock-achievement', achId),
    clearAchievement: (achId) => ipcRenderer.invoke('steam-clear-achievement', achId),
    resetAllStats: () => ipcRenderer.invoke('steam-reset-all-stats'),
    cloudWrite: (filename, data) => ipcRenderer.invoke('steam-cloud-write', filename, data),
    cloudRead: (filename) => ipcRenderer.invoke('steam-cloud-read', filename),
    isSteamDeck: process.argv.includes('--steam-deck'),
    openExternal: (url) => ipcRenderer.invoke('open-external', url),
});
