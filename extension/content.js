// Store the last selection so it survives focus changes when the user clicks the side panel button
let lastSelection = "";

document.addEventListener("selectionchange", () => {
    const sel = window.getSelection().toString();
    if (sel.trim()) {
        lastSelection = sel;
    }
});

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "get_html") {
        sendResponse({ html: document.documentElement.outerHTML, url: window.location.href });
    } else if (request.action === "get_page_text") {
        sendResponse({ text: document.body.innerText, url: window.location.href });
    } else if (request.action === "get_selected_text") {
        // Use stored selection - survives focus changes when side panel button is clicked
        const current = window.getSelection().toString();
        sendResponse({ text: current || lastSelection });
    }
    return true;
});
