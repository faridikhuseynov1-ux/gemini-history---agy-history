#!/usr/bin/env python3
"""
deep_resume.py — Deep Conversation Analyzer & Resumption Context Builder
Reads the FULL transcript of a conversation, extracts everything meaningful,
and builds a rich context document that lets AGY truly continue the session.

Usage:
    python deep_resume.py <conversation_id_or_prefix>
    python deep_resume.py <id> --raw          # Also dump raw exchanges
    python deep_resume.py <id> --no-tools     # Skip tool call details
"""

import os
import json
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

BRAIN_DIR = Path.home() / ".gemini" / "antigravity-cli" / "brain"

# ── Helpers ──────────────────────────────────────────────────────────────────

def clean(text: str) -> str:
    """Strip AGY system XML tags and normalize whitespace."""
    if not text:
        return ""
    text = re.sub(r"<USER_REQUEST>\s*", "", text)
    text = re.sub(r"\s*</USER_REQUEST>", "", text)
    text = re.sub(r"<ADDITIONAL_METADATA>.*?</ADDITIONAL_METADATA>", "", text, flags=re.DOTALL)
    text = re.sub(r"<[A-Z_]+>\s*", "", text)
    text = re.sub(r"\s*</[A-Z_]+>", "", text)
    text = re.sub(r"\{\{.*?\}\}", "", text, flags=re.DOTALL)  # Remove checkpoint markers
    text = re.sub(r"\n{4,}", "\n\n", text)
    return text.strip()


def extract_text(content) -> str:
    """Extract plain text from a step content (str or list)."""
    if isinstance(content, str):
        return clean(content)
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                t = item.get("text") or item.get("content") or ""
                if t:
                    parts.append(str(t))
        return clean(" ".join(parts))
    return clean(str(content))


def fmt_ts(ts: str) -> str:
    if not ts:
        return ""
    try:
        ts = str(ts).replace("Z", "+00:00")
        dt = datetime.fromisoformat(ts)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(ts)[:19]


def find_conv(partial_id: str) -> Path:
    """Find conversation directory by full or partial ID."""
    exact = BRAIN_DIR / partial_id
    if exact.exists():
        return exact
    matches = [d for d in BRAIN_DIR.iterdir()
               if d.is_dir() and d.name.startswith(partial_id)]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        ids = "\n  ".join(m.name for m in matches)
        print(f"[ERROR] Ambiguous prefix '{partial_id}', matches:\n  {ids}", file=sys.stderr)
        sys.exit(1)
    print(f"[ERROR] Conversation not found: {partial_id}", file=sys.stderr)
    sys.exit(1)


# ── Transcript Loader ─────────────────────────────────────────────────────────

def load_full_transcript(conv_dir: Path) -> list[dict]:
    """Load the full (untruncated) transcript."""
    # Prefer full transcript, fall back to regular
    for fname in ("transcript_full.jsonl", "transcript.jsonl"):
        path = conv_dir / ".system_generated" / "logs" / fname
        if path.exists():
            steps = []
            with open(path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        steps.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
            if steps:
                print(f"[INFO] Loaded {len(steps)} steps from {fname}", file=sys.stderr)
                return steps
    print(f"[ERROR] No transcript found in {conv_dir}", file=sys.stderr)
    sys.exit(1)


# ── Conversation Analyzer ─────────────────────────────────────────────────────

class ConversationAnalyzer:
    def __init__(self, steps: list[dict], conv_id: str):
        self.steps = steps
        self.conv_id = conv_id
        self.user_messages: list[dict] = []
        self.agent_responses: list[dict] = []
        self.tool_calls: list[dict] = []
        self.files_read: list[str] = []
        self.files_written: list[str] = []
        self.commands_run: list[str] = []
        self.errors: list[str] = []
        self.checkpoints: list[str] = []
        self.all_exchanges: list[dict] = []

    def analyze(self):
        for step in self.steps:
            stype = step.get("type", "")
            source = step.get("source", "")
            content = extract_text(step.get("content", ""))
            ts = step.get("created_at") or step.get("timestamp", "")

            if not content:
                continue

            if stype == "USER_INPUT" and source in ("USER_EXPLICIT", "USER_QUEUED"):
                if len(content) > 3:
                    entry = {"ts": ts, "text": content}
                    self.user_messages.append(entry)
                    self.all_exchanges.append({"role": "USER", "ts": ts, "text": content})

            elif stype == "PLANNER_RESPONSE":
                if len(content) > 10:
                    entry = {"ts": ts, "text": content}
                    self.agent_responses.append(entry)
                    self.all_exchanges.append({"role": "AGENT", "ts": ts, "text": content})

            elif stype == "VIEW_FILE":
                # Extract file path from content
                m = re.search(r"File Path: `file://(.+?)`", content)
                if m:
                    fp = m.group(1).strip()
                    if fp not in self.files_read:
                        self.files_read.append(fp)

            elif stype in ("WRITE_FILE", "CREATE_FILE"):
                m = re.search(r"(?:File Path|Target):\s*`?(.+?)`?\n", content)
                if m:
                    fp = m.group(1).strip()
                    if fp not in self.files_written:
                        self.files_written.append(fp)
                # Also scan for "Created file" pattern
                for match in re.finditer(r"Created file.*?`([^`]+)`", content):
                    fp = match.group(1)
                    if fp not in self.files_written:
                        self.files_written.append(fp)

            elif stype == "CODE_ACTION":
                # Extract command from code action
                m = re.search(r"CommandLine:\s*(.+?)(?:\n|$)", content)
                if m:
                    cmd = m.group(1).strip()[:120]
                    self.commands_run.append(cmd)

            elif stype == "GENERIC":
                # Sometimes GENERIC contains file write confirmations
                for match in re.finditer(r"Created file.*?`([^`]+)`", content):
                    fp = match.group(1)
                    if fp not in self.files_written:
                        self.files_written.append(fp)

            elif stype == "ERROR_MESSAGE":
                if len(content) > 5:
                    self.errors.append(content[:200])

            elif stype == "CHECKPOINT":
                if "summary" in content.lower() or len(content) > 50:
                    self.checkpoints.append(content[:500])

        return self

    def get_summary(self) -> dict:
        first_ts = ""
        last_ts = ""
        for s in self.steps:
            ts = s.get("created_at") or s.get("timestamp", "")
            if ts:
                if not first_ts:
                    first_ts = ts
                last_ts = ts

        # Determine main topic from first few user messages
        topic_hint = ""
        if self.user_messages:
            topic_hint = self.user_messages[0]["text"][:300]

        # Last user question
        last_user = self.user_messages[-1]["text"] if self.user_messages else ""
        # Last agent response
        last_agent = self.agent_responses[-1]["text"] if self.agent_responses else ""

        return {
            "conv_id": self.conv_id,
            "started": fmt_ts(first_ts),
            "last_activity": fmt_ts(last_ts),
            "user_messages_count": len(self.user_messages),
            "agent_responses_count": len(self.agent_responses),
            "total_steps": len(self.steps),
            "topic_hint": topic_hint,
            "first_user_msg": self.user_messages[0]["text"] if self.user_messages else "",
            "last_user_msg": last_user,
            "last_agent_msg": last_agent,
            "files_read": self.files_read[:30],
            "files_written": self.files_written[:30],
            "commands_run": self.commands_run[:20],
            "errors": self.errors[:5],
        }


# ── Context Document Builder ──────────────────────────────────────────────────

def build_context_document(analyzer: ConversationAnalyzer, args) -> str:
    s = analyzer.get_summary()
    exchanges = analyzer.all_exchanges

    lines = []
    sep = "═" * 72

    lines.append(sep)
    lines.append("  🔄  FULL CONVERSATION CONTEXT — READY TO RESUME")
    lines.append(sep)
    lines.append("")
    lines.append(f"  Conversation ID   : {s['conv_id']}")
    lines.append(f"  Started           : {s['started']}")
    lines.append(f"  Last activity     : {s['last_activity']}")
    lines.append(f"  User messages     : {s['user_messages_count']}")
    lines.append(f"  Agent responses   : {s['agent_responses_count']}")
    lines.append(f"  Total steps       : {s['total_steps']}")
    lines.append("")

    # ── Files changed ─────────────────────────────────────────────────────────
    if s["files_written"]:
        lines.append("─" * 72)
        lines.append("  📝  FILES CREATED / MODIFIED IN THIS SESSION:")
        for fp in s["files_written"]:
            lines.append(f"    • {fp}")
        lines.append("")

    if s["files_read"] and not args.no_tools:
        lines.append("  👁  FILES INSPECTED:")
        for fp in s["files_read"][:15]:
            lines.append(f"    • {fp}")
        lines.append("")

    if s["commands_run"] and not args.no_tools:
        lines.append("─" * 72)
        lines.append("  ⚡  COMMANDS EXECUTED:")
        for cmd in s["commands_run"][:10]:
            lines.append(f"    $ {cmd}")
        lines.append("")

    if s["errors"]:
        lines.append("─" * 72)
        lines.append("  ⚠️  ERRORS ENCOUNTERED:")
        for err in s["errors"]:
            lines.append(f"    ! {err[:150]}")
        lines.append("")

    # ── Full dialogue ─────────────────────────────────────────────────────────
    lines.append("═" * 72)
    lines.append("  💬  FULL CONVERSATION TRANSCRIPT")
    lines.append("═" * 72)
    lines.append("")

    for ex in exchanges:
        role = ex["role"]
        ts_str = f"  [{fmt_ts(ex['ts'])}]" if ex["ts"] else ""
        if role == "USER":
            lines.append(f"👤 USER{ts_str}")
            icon = "  "
        else:
            lines.append(f"🤖 AGY{ts_str}")
            icon = "  "

        text = ex["text"]
        if not args.raw and len(text) > 2000:
            text = text[:2000] + "\n  …[truncated — use --raw for full text]"

        for line in text.split("\n"):
            lines.append(f"{icon}{line}")
        lines.append("")

    # ── Resume context block ──────────────────────────────────────────────────
    lines.append("═" * 72)
    lines.append("  📋  AGENT RESUME INSTRUCTIONS")
    lines.append("═" * 72)
    lines.append("")
    lines.append("You are resuming a conversation. Here is what you MUST do:")
    lines.append("")
    lines.append("1. READ the full transcript above carefully.")
    lines.append("2. UNDERSTAND the complete context: what the user wanted,")
    lines.append("   what you built/did/discussed, what state things are in.")
    lines.append("3. ACKNOWLEDGE what was accomplished and what's pending.")
    lines.append("4. ASK the user how they'd like to continue — or if the last")
    lines.append("   user message is a clear request, proceed with it immediately.")
    lines.append("")
    lines.append("  ─── LAST USER MESSAGE ───")
    lines.append(f"  {s['last_user_msg'][:400]}")
    lines.append("")
    lines.append("  ─── LAST AGENT RESPONSE (summary) ───")
    lines.append(f"  {s['last_agent_msg'][:400]}")
    lines.append("")
    lines.append("  ─── WHAT TO SAY NOW ───")
    lines.append("  Start with: 'Продолжаю с того места, где мы остановились.'")
    lines.append("  Then summarize what was done and what's next.")
    lines.append("")
    lines.append(sep)

    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="Deep conversation analyzer for AGY")
    p.add_argument("conversation_id", help="Full or partial conversation UUID")
    p.add_argument("--raw", action="store_true", help="Include full untruncated text")
    p.add_argument("--no-tools", action="store_true", help="Skip tool call details")
    p.add_argument("--json", action="store_true", help="Output summary as JSON")
    p.add_argument("--out", type=str, default="", help="Write output to file instead of stdout")
    return p.parse_args()


def main():
    args = parse_args()

    conv_dir = find_conv(args.conversation_id)
    conv_id = conv_dir.name

    print(f"[INFO] Analyzing conversation: {conv_id}", file=sys.stderr)
    steps = load_full_transcript(conv_dir)

    analyzer = ConversationAnalyzer(steps, conv_id)
    analyzer.analyze()

    if args.json:
        print(json.dumps(analyzer.get_summary(), indent=2, ensure_ascii=False))
        return

    doc = build_context_document(analyzer, args)

    if args.out:
        out_path = Path(args.out)
        out_path.write_text(doc, encoding="utf-8")
        print(f"[INFO] Context written to: {out_path}", file=sys.stderr)
    else:
        print(doc)


if __name__ == "__main__":
    main()
