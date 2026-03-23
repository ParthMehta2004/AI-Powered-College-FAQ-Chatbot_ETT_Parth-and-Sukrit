const API_URL = "http://127.0.0.1:8000/ask"; // change later for deployment

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
    const question = input.value;

    if (!question) return;

    chatHistory.push({ type: "user", text: "You: " + question });
    renderChat();

    input.value = "";

    try {
        const res = await fetch(API_URL + "?question=" + encodeURIComponent(question), {
            method: "POST"
        });

        const data = await res.json();

        chatHistory.push({ type: "bot", text: "Bot: " + data.answer });
        localStorage.setItem("chatHistory", JSON.stringify(chatHistory));

        renderChat();
    } catch (err) {
        chatHistory.push({ type: "bot", text: "Error connecting to server" });
        renderChat();
    }
}

renderChat();
