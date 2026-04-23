<template>

<div class="chat-toggle" @click="toggleChat">💬</div>

<div v-if="isOpen" class="chat-container">

  <div class="chat-header">
    <span>🤖 AI Assistant</span>
    <span class="chat-status" :class="{ online: isOnline }">
      {{ isOnline ? '● live' : '⚠ offline' }}
    </span>
  </div>

  <div class="chat-messages" ref="messagesEl">
    <div v-for="msg in messages" :key="msg.id" :class="['message', msg.type]">
      {{ msg.text }}
    </div>
    <div v-if="typing" class="message bot typing">
      <span class="dot"></span><span class="dot"></span><span class="dot"></span>
    </div>
  </div>

  <div class="chat-input">
    <input
      v-model="userInput"
      placeholder="Ask about the dashboard..."
      @keyup.enter="sendMessage"
      :disabled="typing"
    />
    <button @click="sendMessage" :disabled="typing || !userInput.trim()">Send</button>
  </div>

</div>

</template>

<script>
const API_BASE = "http://localhost:8000"

export default {

data() {
  return {
    isOpen:   false,
    typing:   false,
    isOnline: false,
    userInput: "",
    // history stores {role, content} objects for the API
    history: [],
    messages: [
      {
        id:   1,
        type: "bot",
        text: "Hello! I'm connected to the live sensor data. Ask me anything about air quality, temperature, CO₂, smoke detection, or health recommendations."
      }
    ]
  }
},

methods: {

  toggleChat() {
    this.isOpen = !this.isOpen
    if (this.isOpen) this.$nextTick(() => this.scrollToBottom())
  },

  async sendMessage() {
    const text = this.userInput.trim()
    if (!text || this.typing) return

    // Show user message
    this.messages.push({ id: Date.now(), type: "user", text })
    this.userInput = ""
    this.typing    = true
    this.$nextTick(() => this.scrollToBottom())

    try {
      const res = await fetch(`${API_BASE}/api/chat`, {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          // Send history as array of {role, content} objects
          history: this.history.slice(-10)
        })
      })

      if (!res.ok) {
        const err = await res.json()
        throw new Error(err.detail || "API error")
      }

      const data  = await res.json()
      const reply = data.reply

      // Add to UI
      this.messages.push({ id: Date.now() + 1, type: "bot", text: reply })

      // Update history for multi-turn
      this.history.push({ role: "user",      content: text  })
      this.history.push({ role: "assistant", content: reply })

      this.isOnline = true

    } catch (e) {
      this.messages.push({
        id:   Date.now() + 1,
        type: "bot",
        text: "⚠️ Error: " + e.message
      })
      this.isOnline = false
    }

    this.typing = false
    this.$nextTick(() => this.scrollToBottom())
  },

  scrollToBottom() {
    const el = this.$refs.messagesEl
    if (el) el.scrollTop = el.scrollHeight
  }
}

}
</script>

<style scoped>
.chat-toggle {
  position: fixed; bottom: 20px; right: 20px;
  width: 60px; height: 60px;
  background: #2b7cff; color: white; font-size: 25px;
  display: flex; align-items: center; justify-content: center;
  border-radius: 50%; cursor: pointer;
  box-shadow: 0 5px 20px rgba(0,0,0,0.3);
  z-index: 1000; transition: transform 0.2s;
}
.chat-toggle:hover { transform: scale(1.1); }

.chat-container {
  position: fixed; bottom: 90px; right: 20px;
  width: 320px; background: white;
  border-radius: 14px; box-shadow: 0 10px 30px rgba(0,0,0,0.2);
  overflow: hidden; font-family: Arial, sans-serif; z-index: 1000;
}

.chat-header {
  background: #2b7cff; color: white;
  padding: 12px 16px;
  display: flex; justify-content: space-between; align-items: center;
  font-weight: bold;
}

.chat-status { font-size: 11px; opacity: 0.8; }
.chat-status.online { color: #90ee90; }

.chat-messages {
  height: 260px; overflow-y: auto;
  padding: 12px; display: flex; flex-direction: column; gap: 8px;
}

.message {
  max-width: 85%; padding: 8px 12px;
  border-radius: 12px; font-size: 13px;
  line-height: 1.4; word-wrap: break-word;
}
.message.user {
  align-self: flex-end;
  background: #2b7cff; color: white;
  border-bottom-right-radius: 4px;
}
.message.bot {
  align-self: flex-start;
  background: #f1f3f4; color: #333;
  border-bottom-left-radius: 4px;
}

.typing { display: flex; align-items: center; gap: 4px; padding: 10px 14px; }
.dot { width: 7px; height: 7px; background: #888; border-radius: 50%; animation: bounce 1.2s infinite; }
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce {
  0%, 80%, 100% { transform: translateY(0); }
  40%           { transform: translateY(-6px); }
}

.chat-input { display: flex; border-top: 1px solid #eee; }
.chat-input input { flex: 1; padding: 10px 12px; border: none; outline: none; font-size: 13px; }
.chat-input button {
  background: #2b7cff; color: white;
  border: none; padding: 10px 14px; cursor: pointer; font-size: 13px;
}
.chat-input button:disabled { background: #aaa; cursor: not-allowed; }
.chat-input button:hover:not(:disabled) { background: #1a6aee; }
</style>