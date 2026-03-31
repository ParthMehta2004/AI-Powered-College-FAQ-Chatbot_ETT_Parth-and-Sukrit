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

async function warmUpServer() {
    try {
        // Use no-cors mode for warmup ping to avoid CORS preflight failure
        await fetch(API_URL + "/health", { method: "GET", mode: "no-cors" });
    } catch (e) {
        // silently ignore
    }
}

async function sendMessage() {
    const input = document.getElementById("user-input");
    const question = input.value.trim();
    if (!question) return;

    chatHistory.push({ type: "user", text: "You: " + question });
    input.value = "";

    chatHistory.push({ type: "bot", text: "Bot: Thinking... (may take up to 90s if server just woke up)" });
    renderChat();

    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 120000); // 120 seconds

    try {
        const res = await fetch(API_URL + "/ask?question=" + encodeURIComponent(question), {
            method: "POST",
            signal: controller.signal
        });
        clearTimeout(timeout);

        const data = await res.json();
        chatHistory.pop();
        chatHistory.push({ type: "bot", text: "Bot: " + (data.answer || "No answer returned.") });

    } catch (err) {
        clearTimeout(timeout);
        chatHistory.pop();
        if (err.name === "AbortError") {
            chatHistory.push({ type: "bot", text: "Bot: Server is waking up. Please try again in 30 seconds." });
        } else {
            chatHistory.push({ type: "bot", text: "Bot: Error - " + err.message });
        }
    }

    localStorage.setItem("chatHistory", JSON.stringify(chatHistory));
    renderChat();
}

document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("user-input");
    if (input) {
        input.addEventListener("keydown", (e) => {
            if (e.key === "Enter") sendMessage();
        });
    }
    warmUpServer();
});

renderChat();
