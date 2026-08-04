---
name: history-browser
description: >-
  Activate when the user types /history, says "show history", "list
  conversations", "resume a conversation", "continue from where I left off",
  gives a conversation ID, or any similar request to browse or restore a
  past AGY session. This skill shows history and enables TRUE deep resumption
  by reading the complete transcript and continuing the session as if it never
  ended.
---

# History Browser — Deep Conversation Resumption

This skill lets you **list** past conversations and **truly resume** them by
reading the entire transcript and picking up exactly where you left off.

---

## STEP 1 — List Conversations

When the user wants to browse history, run:

```bash
python3 ~/.gemini/skills/history-browser/scripts/list_conversations.py
```

Options:
- `--limit N` — show N conversations (default: 30)
- `--search KEYWORD` — filter by keyword in messages
- `--json` — machine-readable output

**Show the list to the user** and ask: _"Which conversation do you want to
continue? Pick a number or give me the ID."_

---

## STEP 2 — Deep Resume (CRITICAL — read this carefully)

When the user picks a conversation to resume, you MUST do the following **in
order**:

### 2a. Run the deep analyzer

```bash
python3 ~/.gemini/skills/history-browser/scripts/resume_conversation.py <ID>
```

This will print the FULL conversation transcript — every user message, every
agent response, files modified, commands run, errors encountered.

For full untruncated output:
```bash
python3 ~/.gemini/skills/history-browser/scripts/resume_conversation.py <ID> --raw
```

### 2b. READ and INTERNALIZE the entire output

**Do not skim.** Read every user message and every agent response.
Understand:
- What problem the user was solving
- What decisions were made and why
- What code/files were created or changed
- What was left incomplete or in-progress
- What the user last asked for
- What you last said / did

### 2c. Reconstruct the world state

After reading, you know the state of the world. If files were modified, you
can check their current state with `view_file` if needed. If code was being
written, you know where it stands.

### 2d. Continue naturally

**Do NOT** say "I'm an AI and don't have memory of previous sessions."  
**DO** say something like:

> "Продолжаю с того места, где мы остановились."
>
> [Brief summary of what was accomplished]
>
> [What's the next step based on where the conversation ended]
>
> "Продолжаем?"

If the last message was a clear task (e.g., "fix the bug", "add auth"), proceed
with it **immediately** without asking for confirmation.

---

## STEP 3 — Reading the Raw Transcript Directly (Advanced)

If the script output is insufficient, read the transcript file directly:

```
~/.gemini/antigravity-cli/brain/<CONVERSATION_ID>/.system_generated/logs/transcript_full.jsonl
```

Use `view_file` to read it. Each line is a JSON step with:
- `type`: `USER_INPUT` | `PLANNER_RESPONSE` | `VIEW_FILE` | `CODE_ACTION` | …
- `source`: `USER_EXPLICIT` | `MODEL` | `SYSTEM` | …
- `content`: the actual text (string or list of parts)
- `created_at`: ISO 8601 timestamp

Focus on `USER_INPUT` (what the user said) and `PLANNER_RESPONSE` (what you
said/did).

---

## Rules for True Resumption

1. **Never claim you can't remember** — you have the full transcript.
2. **Never ask the user to re-explain** what they already explained.
3. **Pick up mid-task** if there was an incomplete task in progress.
4. **Reference specific things** from the conversation to show you truly read it.
5. **If files were modified**, check them with `view_file` before continuing.
6. **Match the tone** of the previous conversation (formal/informal, language).

---

## Examples of Good Resumption

**Bad:** "I don't have access to our previous conversation. Could you remind me what we were working on?"

**Good:** "Продолжаю с того места. Мы разрабатывали FastAPI бэкенд для системы чатов. Ты попросил добавить JWT аутентификацию. Я как раз начал писать `auth.py` — продолжу с этого момента."

**Bad:** "How can I help you today?"

**Good:** "Помню, мы остановились на баге в компоненте `MessageList.tsx` — у нас не рендерились сообщения при пустом массиве. Давай сразу к делу — вот фикс:"
