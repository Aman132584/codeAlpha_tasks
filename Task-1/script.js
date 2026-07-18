/* ============================================================
   FAQ Chatbot — frontend only.
   All NLP/matching happens on the backend (your Python code).
   This file just sends the question and renders the answer.

   EXPECTED BACKEND CONTRACT
   --------------------------------------------------------------
   POST /api/ask
   Request body  (JSON): { "question": "How do I reset my password?" }
   Response body (JSON): {
     "answer": "Go to Settings, then Account, then Change password.",
     "matched_question": "How do I change my password?",  // optional
     "score": 0.82                                          // optional, 0-1
   }
   If no good match is found, respond with:
   { "answer": null }
   or any answer string you want to show as a fallback message.
   ============================================================ */

const API_URL = "http://127.0.0.1:5000/api/ask"; // change this if your backend runs elsewhere,
                             // e.g. "http://localhost:5000/api/ask"

const SUGGESTIONS = [
  "How much does it cost?",
  "Can I use it offline?",
  "How do I share a list?",
  "Is my data secure?",
];

const messagesEl = document.getElementById("messages");
const formEl = document.getElementById("chatForm");
const inputEl = document.getElementById("chatInput");
const resetBtn = document.getElementById("resetBtn");

function renderUserMessage(text) {
  const row = document.createElement("div");
  row.className = "lc-row lc-row-user";
  row.innerHTML = `<div class="lc-bubble lc-bubble-user"></div>`;
  row.querySelector(".lc-bubble").textContent = text;
  messagesEl.appendChild(row);
  scrollToBottom();
}

function renderBotMessage(answer, matchedQuestion, score) {
  const row = document.createElement("div");
  row.className = "lc-row lc-row-bot";

  const bubble = document.createElement("div");
  bubble.className = "lc-bubble lc-bubble-bot";
  bubble.textContent = answer;
  row.appendChild(bubble);

  if (matchedQuestion) {
    const meta = document.createElement("div");
    meta.className = "lc-meta";
    const pct = typeof score === "number" ? ` · ${Math.round(score * 100)}% confidence` : "";
    meta.textContent = `Matched "${matchedQuestion}"${pct}`;
    row.appendChild(meta);
  }

  messagesEl.appendChild(row);
  scrollToBottom();
}

function renderTypingIndicator() {
  const row = document.createElement("div");
  row.className = "lc-row lc-row-bot";
  row.id = "typingRow";
  row.innerHTML = `
    <div class="lc-bubble lc-bubble-bot lc-typing">
      <span class="lc-dot"></span><span class="lc-dot"></span><span class="lc-dot"></span>
    </div>`;
  messagesEl.appendChild(row);
  scrollToBottom();
}

function removeTypingIndicator() {
  const row = document.getElementById("typingRow");
  if (row) row.remove();
}

function renderSuggestions() {
  const wrap = document.createElement("div");
  wrap.className = "lc-suggestions";
  wrap.id = "suggestionsRow";
  SUGGESTIONS.forEach((s) => {
    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = "lc-chip";
    chip.textContent = s;
    chip.addEventListener("click", () => sendMessage(s));
    wrap.appendChild(chip);
  });
  messagesEl.appendChild(wrap);
  scrollToBottom();
}

function removeSuggestions() {
  const row = document.getElementById("suggestionsRow");
  if (row) row.remove();
}

function scrollToBottom() {
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

async function sendMessage(text) {
  const question = text.trim();
  if (!question) return;

  removeSuggestions();
  renderUserMessage(question);
  inputEl.value = "";
  renderTypingIndicator();

  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const data = await res.json();

    removeTypingIndicator();

    if (!data || !data.answer) {
      renderBotMessage("Hmm, I couldn't find a confident match for that. Try rephrasing, or tap a topic below.");
      renderSuggestions();
    } else {
      renderBotMessage(data.answer, data.matched_question, data.score);
    }
  } catch (err) {
    removeTypingIndicator();
    renderBotMessage("Sorry, I couldn't reach the server. Is the backend running?");
    console.error(err);
  }
}

formEl.addEventListener("submit", (e) => {
  e.preventDefault();
  sendMessage(inputEl.value);
});

resetBtn.addEventListener("click", () => {
  messagesEl.innerHTML = "";
  renderBotMessage("Hi! I'm the Listly FAQ bot. Ask me something about your account, or tap a suggestion below.");
  renderSuggestions();
});

// initial greeting
renderBotMessage("Hi! I'm the Listly FAQ bot. Ask me something about your account, or tap a suggestion below.");
renderSuggestions();
