import React, { useState, useRef, useEffect } from "react";
import { Send } from "lucide-react";
import * as anime from "animejs";  // << Import anime.js here
import "./App.css";

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const messagesEndRef = useRef(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMsg = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMsg.text }),
      });
      const data = await res.json();
      const botMsg = { sender: "bot", text: data.reply };
      setMessages((prev) => [...prev, botMsg]);
    } catch (error) {
      console.error("Error fetching reply:", error);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") sendMessage();
  };

  return (
    <div className="container">
      <div className="chatbox">
        <div className="header">UBIBI Enrollment Chatbot</div>
        <div className="messages">
          {messages.map((msg, idx) => (
            <ChatMessage key={idx} msg={msg} />
          ))}
          <div ref={messagesEndRef} />
        </div>
        <div className="input-area">
          <input
            type="text"
            placeholder="Type your message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            className="input"
          />
          <button onClick={sendMessage} className="send-button">
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );
}

function ChatMessage({ msg }) {
  const isUser = msg.sender === "user";

  return (
    <div className={`message ${isUser ? "user" : "bot"}`}>
      <div className="bubble">
        {msg.text}
      </div>
    </div>
  );
}
