const API_URL = "https://ai-powered-college-faq-chatbot-ett-parth.onrender.com";

let chatHistory = JSON.parse(localStorage.getItem("chatHistory")) || [];

function renderChat() {
    const chatBox = document.getElementById("chat-box");
    chatBox.innerHTML = "";
    chatHistory.forEach(msg => {
        const div = document.createElement("div");
        div.className = msg.type;
        div.innerText = msg.text;
        chatBox.appendChild(div);
    });
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Ping the server on page load so it wakes up before user asks anything
async function warmUpServer() {
    try {
        await fetch(API_URL + "/", { method: "GET" });
    } catch (e) {
        // silently ignore - just a warm-up
    }
}

async function sendMessage() {
    const input = document.getElementById("user-input");
    const question = input.value.trim();
    if (!question) return;

    chatHistory.push({ type: "user", text: "You: " + question });
    input.value = "";

    chatHistory.push({ type: "bot", text: "Bot: Thinking... (may take up to 60s on first load)" });
    renderChat();

    // 60 second timeout to handle Render cold start
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 120000);

    try {
        const res = await fetch(API_URL + "/ask?question=" + encodeURIComponent(question), {
            method: "POST",
            signal: controller.signal
        });
        clearTimeout(timeout);

        const data = await res.json();

        chatHistory.pop(); // remove Thinking...
        chatHistory.push({ type: "bot", text: "Bot: " + (data.answer || "No answer returned.") });

    } catch (err) {
        clearTimeout(timeout);
        chatHistory.pop(); // remove Thinking...

        if (err.name === "AbortError") {
            chatHistory.push({ type: "bot", text: "Bot: Request timed out. Please try again in 30 seconds." });
        } else {
            chatHistory.push({ type: "bot", text: "Bot: Error connecting to server. Please try again." });
        }
    }

    localStorage.setItem("chatHistory", JSON.stringify(chatHistory));
    renderChat();
}

// Enter key support
document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("user-input");
    if (input) {
        input.addEventListener("keydown", (e) => {
            if (e.key === "Enter") sendMessage();
        });
    }
    warmUpServer(); // wake up Render on page load
});

renderChat();
