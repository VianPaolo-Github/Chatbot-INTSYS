import React, { useState, useRef, useEffect } from "react";
import { Send } from "lucide-react";
import "./App.css";

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMsg = { sender: "user", text: input };
    setMessages(prev => [...prev, userMsg]);
    setInput("");

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMsg.text }),
      });
      const data = await res.json();
      const botMsg = { sender: "bot", text: data.reply };
      setMessages(prev => [...prev, botMsg]);
    } catch (error) {
      console.error("Error fetching reply:", error);
    }
  };

  const handleKeyPress = e => {
    if (e.key === "Enter") sendMessage();
  };

  return (
    <div className="container">
      <div className="chatbox">
        <div className="header">UB Enrollment Chatbot</div>
        <div className="messages">
          {messages.map((msg, idx) => (
            <div key={idx} className={msg.sender === "user" ? "message user" : "message bot"}>
              {msg.text}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
        <div className="input-area">
          <input
            type="text"
            placeholder="Type your message..."
            value={input}
            onChange={e => setInput(e.target.value)}
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