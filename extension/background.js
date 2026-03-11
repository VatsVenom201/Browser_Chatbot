chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true }).catch((error) => console.error(error));

chrome.runtime.onInstalled.addListener(() => {
    chrome.storage.local.set({ session_id: crypto.randomUUID() });
});
