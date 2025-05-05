import React, { useState, useRef, useEffect } from "react";
import { Send } from "lucide-react";
import "./App.css";

export default function App() {
  const [messages, setMessages] = useState([
    { sender: 'bot', text: "Hello! I'm here to help. You can chat or upload an essay for analysis." }
  ]);
  const [input, setInput] = useState("");
  const messagesEndRef = useRef(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
  
    const formData = new FormData();
    formData.append("file", file);
  
    try {
      const response = await fetch("http://localhost:8000/upload-essay", {
        method: "POST",
        body: formData,
      });
  
      const data = await response.json();
  
      if (data.error) {
        setMessages((prev) => [...prev, { sender: "bot", text: `❌ Error: ${data.error}` }]);
      } else {
        setMessages((prev) => [
          ...prev,
          { sender: "user", text: `📄 Uploaded essay: ${file.name}` },
          { sender: "bot", text: `📝 Summary: ${data.summary}` },
        ]);
      }
    } catch (error) {
      setMessages((prev) => [...prev, { sender: "bot", text: `⚠️ Failed to upload essay.` }]);
    }
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
        <div className="input-container">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            placeholder="Type your message here..."
            className="chat-input"
          />
          <input
            type="file"
            id="file-upload"
            accept=".pdf,.docx,.txt"
            onChange={handleFileUpload}
            style={{ display: "none" }}
          />
          <button
            className="icon-button"
            onClick={() => document.getElementById("file-upload").click()}
            title="Upload Essay"
          >
            📎
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
