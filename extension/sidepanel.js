const API_BASE = "http://127.0.0.1:8000"; // Dev. For production: "https://your-render-url.onrender.com"
let sessionId = crypto.randomUUID();

// Persist session ID across panel opens
chrome.storage.local.get(["session_id"], (result) => {
    if (result.session_id) {
        sessionId = result.session_id;
    } else {
        chrome.storage.local.set({ session_id: sessionId });
    }
});

// ---- Helper: append a message bubble ----
// If id is given and the element already exists, update it in-place instead of creating a new one
function appendMessage(role, text, id = null) {
    const chatBox = document.getElementById("chat-box");
    let msgDiv = id ? document.getElementById(id) : null;

    if (!msgDiv) {
        msgDiv = document.createElement("div");
        msgDiv.className = `message ${role === "user" ? "user-message" : "ai-message"}`;
        if (id) msgDiv.id = id;
        chatBox.appendChild(msgDiv);
    }

    msgDiv.textContent = text;
    chatBox.scrollTop = chatBox.scrollHeight;
    return msgDiv;
}

// ---- Helper: set loading state ----
function setLoading(visible) {
    document.getElementById("loading").classList.toggle("hidden", !visible);
}

// ---- Analyze Page ----
document.getElementById("analyze-btn").addEventListener("click", async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    chrome.tabs.sendMessage(tab.id, { action: "get_html" }, async (response) => {
        if (chrome.runtime.lastError || !response) {
            appendMessage("ai", "Please refresh the webpage and try again.");
            return;
        }

        setLoading(true);
        try {
            const res = await fetch(`${API_BASE}/analyze`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    session_id: sessionId,
                    html: response.html,
                    url: response.url
                })
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();
            appendMessage("ai", `✅ Page analyzed! Created ${data.num_chunks} chunks. You can now ask questions about it.`);
        } catch (e) {
            appendMessage("ai", `Error analyzing page: ${e.message}`);
        } finally {
            setLoading(false);
        }
    });
});

// ---- Core summarize function ----
async function summarize(text) {
    if (!text || !text.trim()) {
        appendMessage("ai", "No readable text found on this page.");
        return;
    }

    setLoading(true);
    const msgId = `msg-${Date.now()}`;
    // Create the message bubble BEFORE fetching so we hold a stable reference
    const msgDiv = appendMessage("ai", "Summarizing...", msgId);

    try {
        const res = await fetch(`${API_BASE}/summarize`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                session_id: sessionId,
                text: text,
                mode: "selected_text"   // backend just truncates & sends to Groq either way
            })
        });

        if (!res.ok) {
            msgDiv.textContent = `Error: Server returned ${res.status}`;
            return;
        }

        const fullText = await res.text();
        msgDiv.textContent = fullText.trim() || "(No summary returned — try again in a few seconds)";
        document.getElementById("chat-box").scrollTop = document.getElementById("chat-box").scrollHeight;
    } catch (e) {
        msgDiv.textContent = `Error: ${e.message}`;
        console.error("Summarize error:", e);
    } finally {
        setLoading(false);
    }
}

// ---- Summarize Page ----
document.getElementById("summarize-page-btn").addEventListener("click", async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    if (!tab.url || tab.url.startsWith("chrome://") || tab.url.startsWith("edge://") || tab.url.startsWith("chrome-extension://")) {
        appendMessage("ai", "I cannot read Chrome's internal pages. Open a normal website.");
        return;
    }

    try {
        // executeScript injects JS on demand - no page refresh needed after extension updates
        const results = await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            func: () => document.body.innerText
        });
        const pageText = results[0]?.result || "";
        await summarize(pageText);
    } catch (e) {
        appendMessage("ai", `Could not read page: ${e.message}. Try refreshing the page.`);
    }
});

// ---- Summarize Selected Text ----
document.getElementById("summarize-selected-btn").addEventListener("click", async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    
    // Use sendMessage - content.js stores the last selection on selectionchange
    // so it survives focus shifts when the side panel button is clicked
    chrome.tabs.sendMessage(tab.id, { action: "get_selected_text" }, async (response) => {
        if (chrome.runtime.lastError) {
            appendMessage("ai", "Please refresh the page and try again.");
            return;
        }
        if (!response || !response.text || !response.text.trim()) {
            alert("No text selected. Please highlight some text on the page first.");
            return;
        }
        await summarize(response.text);
    });
});

// ---- Chat ----
document.getElementById("send-btn").addEventListener("click", async () => {
    const input = document.getElementById("user-input");
    const question = input.value.trim();
    if (!question) return;

    input.value = "";
    appendMessage("user", question);

    setLoading(true);
    const msgId = `msg-${Date.now()}`;
    const msgDiv = appendMessage("ai", "Thinking...", msgId);

    try {
        const res = await fetch(`${API_BASE}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                session_id: sessionId,
                question: question
            })
        });

        if (!res.ok) {
            msgDiv.textContent = `Error: Server returned ${res.status}`;
            return;
        }

        const fullText = await res.text();
        msgDiv.textContent = fullText.trim() || "(Empty response — please try again)";
        document.getElementById("chat-box").scrollTop = document.getElementById("chat-box").scrollHeight;

    } catch (e) {
        msgDiv.textContent = `Error: ${e.message}`;
        console.error("Chat error:", e);
    } finally {
        setLoading(false);
    }
});

// ---- Enter key to send ----
document.getElementById("user-input").addEventListener("keypress", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        document.getElementById("send-btn").click();
    }
});
