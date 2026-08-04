# agy-history 📚

> **Antigravity CLI skill** — browse your conversation history and **truly resume** any past session.

When you type `/history` in AGY, this skill lets you:
1. See all your past conversations (sorted by last activity)
2. Pick one and **resume it** — AGY reads the **entire transcript**, understands everything, and continues naturally

---

## ✨ Features

- 📋 **List all past conversations** with date, message count, and first message preview
- 🔍 **Search** by keyword across conversation history
- 🔄 **Deep resume** — reads `transcript_full.jsonl` (full untruncated version), reconstructs complete context
- 📝 Tracks **files modified**, **commands run**, **errors** from the session
- 🔢 Fuzzy ID matching — use first 8 characters of conversation ID
- ⚡ CLI tool `agy-history` available system-wide

---

## 📁 Structure

```
history-browser/
├── SKILL.md                       ← AGY skill instructions (auto-loaded)
└── scripts/
    ├── agy-history                ← Shell CLI wrapper
    ├── list_conversations.py      ← List & search conversations
    └── resume_conversation.py     ← Deep transcript analyzer
```

---

## 🚀 Installation

```bash
# Clone to your global AGY skills directory
git clone https://github.com/faridikhuseynov1-ux/gemini-history---agy-history \
    ~/.gemini/skills/history-browser

# Register globally (if not already done)
cat > ~/.gemini/config/skills.json << 'EOF'
{
  "entries": [
    { "path": "~/.gemini/skills" }
  ]
}
EOF

# Install CLI tool system-wide
chmod +x ~/.gemini/skills/history-browser/scripts/agy-history
sudo ln -sf ~/.gemini/skills/history-browser/scripts/agy-history /usr/local/bin/agy-history
```

---

## 💻 Usage

### In AGY chat

Just type:
```
/history
```
AGY will list your conversations and ask which one to resume.

Or directly:
```
resume conversation 3ee8ab89
continue from where I left off — 3ee8ab89
```

### In Terminal

```bash
# List last 30 conversations
agy-history

# Search by keyword
agy-history --search "docker"

# Show last 50
agy-history --limit 50

# Deep resume — full context (first 8 chars of ID is enough)
agy-history resume 3ee8ab89

# Full untruncated transcript
agy-history resume 3ee8ab89 --raw

# Write context to file
agy-history resume 3ee8ab89 --out /tmp/context.md

# Help
agy-history --help
```

---

## 🧠 How Deep Resume Works

When you resume a conversation, the skill:

1. Loads `transcript_full.jsonl` — the **complete, untruncated** transcript
2. Extracts every **user message** and **agent response**
3. Tracks **files read/written**, **commands executed**, **errors**
4. Builds a rich context document
5. AGY reads it all and **continues naturally** — no re-explaining needed

AGY will say something like:
> *"Продолжаю с того места, где мы остановились. Мы разрабатывали FastAPI бэкенд, ты попросил добавить JWT аутентификацию. Продолжаю..."*

---

## 📋 Requirements

- Antigravity CLI (`agy`) installed
- Python 3.10+
- `~/.gemini/antigravity-cli/brain/` directory (created automatically by AGY)

---

## 📄 License

MIT — use freely, improve, share.
