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

async function sendMessage() {
    const input = document.getElementById("user-input");
    const question = input.value.trim();

    if (!question) return;

    chatHistory.push({ type: "user", text: "You: " + question });
    renderChat();
    input.value = "";

    // Show a loading indicator
    chatHistory.push({ type: "bot", text: "Bot: Thinking..." });
    renderChat();

    try {
        // ✅ FIX: POST to /ask with question as a query param
        const res = await fetch(API_URL + "/ask?question=" + encodeURIComponent(question), {
            method: "POST"
        });

        const data = await res.json();

        // Remove the "Thinking..." message
        chatHistory.pop();

        // ✅ FIX: read data.answer correctly
        chatHistory.push({ type: "bot", text: "Bot: " + (data.answer || "No answer returned.") });
        localStorage.setItem("chatHistory", JSON.stringify(chatHistory));

        renderChat();
    } catch (err) {
        chatHistory.pop(); // remove "Thinking..."
        chatHistory.push({ type: "bot", text: "Bot: Error connecting to server. Please try again." });
        localStorage.setItem("chatHistory", JSON.stringify(chatHistory));
        renderChat();
    }
}

// Allow pressing Enter to send
document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("user-input");
    if (input) {
        input.addEventListener("keydown", (e) => {
            if (e.key === "Enter") sendMessage();
        });
    }
});

renderChat();
