import React, { useState, useEffect } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:5001";

function App() {
    const [messages, setMessages] = useState([]);
    const [username, setUsername] = useState(localStorage.getItem("username") || "");
    const [messageText, setMessageText] = useState("");
    const [searchQuery, setSearchQuery] = useState("");

    // Load messages from server
    useEffect(() => {
        fetchMessages();
        const interval = setInterval(fetchMessages, 3000);
        return () => clearInterval(interval);
    }, []);

    const fetchMessages = async () => {
        try {
            console.log("Fetching latest messages");
            const response = await fetch(`${API_URL}/messages`);
            const data = await response.json();
            setMessages(data);
        } catch (error) {
            console.error("Error fetching messages:", error);
            alert("Failed to load messages.");
        }
    };

    const sendMessage = async () => {
        if (!username.trim()) {
            alert("Please enter a username before sending a message.");
            return;
        }
        if (!messageText.trim()) {
            alert("Cannot send an empty message.");
            return;
        }

        const messageData = {
            content: messageText,
            sender: username,
            timestamp: new Date().toISOString(),
            extra: null
        };

        console.log("Sending message:", messageData);

        try {
            const response = await fetch(`${API_URL}/send`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "authkey 0987654321"
                },
                body: JSON.stringify(messageData)
            });

            const responseText = await response.text();
            console.log("Server Response:", responseText);

            if (response.ok) {
                setMessageText("");
                fetchMessages();
            } else {
                alert(`Failed to send message. Server responded with: ${response.status}`);
            }
        } catch (error) {
            console.error("Error sending message:", error);
            alert("Failed to send message due to a network error.");
        }
    };

    const filteredMessages = messages.filter((msg) =>
        msg.content.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <div className="chat-container">
            <h1>💬 AI & Tech Chat</h1>

            <div className="instructions">
                <h3>How to Use:</h3>
                <p>
                    Use the search bar to find messages.<br />
                    Type a message and hit <span style={{ color: "green", fontWeight: "bold" }}>"Send"</span> to participate in the discussion.<br />
                    Use **[nop]word[/nop]** for bold, *[nop]word[/nop]* for italics.<br />
                    The Message Window is set to 50 messages
                </p>
            </div>


            <div className="chat-controls">
                <input
                    type="text"
                    placeholder="👤 Username"
                    value={username}
                    onChange={(e) => {
                        setUsername(e.target.value);
                        localStorage.setItem("username", e.target.value);
                    }}
                />
                <input
                    type="text"
                    placeholder="🔍 Search messages..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                />
            </div>

            <div className="message-box">
                {filteredMessages.map((msg, index) => (
                    <div key={index} className={`message ${msg.sender === "AIBot" ? "ai-message" : ""}`}>
                        <strong>{msg.sender}:</strong> {msg.content}
                    </div>
                ))}
            </div>

            <div className="message-input">
                <input
                    type="text"
                    placeholder="Type a message..."
                    value={messageText}
                    onChange={(e) => setMessageText(e.target.value)}
                    onKeyPress={(e) => e.key === "Enter" && sendMessage()}
                />
                <button onClick={sendMessage}>Send</button>
            </div>
        </div>
    );
}

export default App;
