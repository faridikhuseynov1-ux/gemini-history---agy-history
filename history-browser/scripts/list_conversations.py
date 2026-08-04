#!/usr/bin/env python3
"""
list_conversations.py — Antigravity History Browser (v2)
Lists all past conversations, sorted by last activity, with rich previews.

Usage:
    python list_conversations.py [--limit N] [--search QUERY] [--json]
"""

import os
import json
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime

BRAIN_DIR = Path.home() / ".gemini" / "antigravity-cli" / "brain"


def parse_args():
    p = argparse.ArgumentParser(description="List past Antigravity conversations")
    p.add_argument("--limit", type=int, default=30, help="Max conversations (default: 30)")
    p.add_argument("--search", type=str, default="", help="Filter by keyword")
    p.add_argument("--json", action="store_true", help="Output as JSON")
    return p.parse_args()


def clean(text: str) -> str:
    text = re.sub(r"<USER_REQUEST>\s*", "", text)
    text = re.sub(r"\s*</USER_REQUEST>", "", text)
    text = re.sub(r"<ADDITIONAL_METADATA>.*?</ADDITIONAL_METADATA>", "", text, flags=re.DOTALL)
    text = re.sub(r"<[A-Z_]+>\s*", "", text)
    text = re.sub(r"\s*</[A-Z_]+>", "", text)
    text = re.sub(r"\{\{.*?\}\}", "", text, flags=re.DOTALL)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def fmt_ts(ts: str, short: bool = False) -> str:
    if not ts:
        return ""
    try:
        ts = str(ts).replace("Z", "+00:00")
        dt = datetime.fromisoformat(ts)
        return dt.strftime("%m/%d %H:%M" if short else "%Y-%m-%d %H:%M")
    except Exception:
        return str(ts)[:16]


def get_conv_info(conv_dir: Path) -> dict | None:
    # Prefer full transcript for accuracy
    transcript = None
    for fname in ("transcript_full.jsonl", "transcript.jsonl"):
        p = conv_dir / ".system_generated" / "logs" / fname
        if p.exists():
            transcript = p
            break
    if not transcript:
        return None

    conv_id = conv_dir.name
    first_user_msg = ""
    last_user_msg = ""
    last_agent_msg = ""
    user_msg_count = 0
    first_ts = ""
    last_ts = ""
    files_written = []
    step_count = 0

    try:
        with open(transcript, encoding="utf-8") as f:
            for raw in f:
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    step = json.loads(raw)
                except json.JSONDecodeError:
                    continue

                step_count += 1
                stype = step.get("type", "")
                source = step.get("source", "")
                ts = step.get("created_at") or step.get("timestamp", "")
                content_raw = step.get("content", "")

                if isinstance(content_raw, list):
                    content = clean(" ".join(
                        p.get("text", "") for p in content_raw
                        if isinstance(p, dict)
                    ))
                else:
                    content = clean(str(content_raw))

                if ts:
                    if not first_ts:
                        first_ts = ts
                    last_ts = ts

                if stype == "USER_INPUT" and source in ("USER_EXPLICIT", "USER_QUEUED"):
                    if content and len(content) > 3:
                        user_msg_count += 1
                        if not first_user_msg:
                            first_user_msg = content
                        last_user_msg = content

                elif stype == "PLANNER_RESPONSE" and content and len(content) > 10:
                    last_agent_msg = content

                elif stype == "GENERIC":
                    for m in re.finditer(r"Created file.*?`([^`]+)`", content):
                        fp = m.group(1)
                        if fp not in files_written:
                            files_written.append(fp)

    except Exception:
        return None

    if not first_user_msg:
        return None

    return {
        "id": conv_id,
        "started": fmt_ts(first_ts),
        "last_active": fmt_ts(last_ts),
        "last_ts_raw": last_ts or first_ts,
        "user_msgs": user_msg_count,
        "steps": step_count,
        "first_msg": first_user_msg[:120],
        "last_user_msg": last_user_msg[:80],
        "last_agent_msg": last_agent_msg[:120],
        "files_written": files_written[:5],
    }


def main():
    args = parse_args()

    if not BRAIN_DIR.exists():
        print(f"[ERROR] Brain directory not found: {BRAIN_DIR}", file=sys.stderr)
        sys.exit(1)

    print("[...] Scanning conversations...", file=sys.stderr)

    raw_list = []
    for conv_dir in BRAIN_DIR.iterdir():
        if not conv_dir.is_dir():
            continue
        info = get_conv_info(conv_dir)
        if info is None:
            continue
        if args.search:
            haystack = (info["first_msg"] + " " + info["last_user_msg"]).lower()
            if args.search.lower() not in haystack:
                continue
        raw_list.append(info)

    # Sort by last activity, newest first
    def sort_key(x):
        ts = x.get("last_ts_raw", "")
        if ts:
            try:
                return datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except Exception:
                pass
        return datetime.min

    raw_list.sort(key=sort_key, reverse=True)
    conversations = raw_list[:args.limit]

    if args.json:
        print(json.dumps(conversations, indent=2, ensure_ascii=False))
        return

    if not conversations:
        print("\n  No conversations found.")
        if args.search:
            print(f"  (searched for: '{args.search}')")
        return

    # ── Pretty output ──────────────────────────────────────────────────────────
    print()
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║           📚  Antigravity Conversation History Browser              ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print()

    for i, conv in enumerate(conversations, 1):
        files_tag = ""
        if conv["files_written"]:
            files_tag = f"  📁 {len(conv['files_written'])} files"

        print(f"  [{i:02d}]  🗓  {conv['last_active']}  │  💬 {conv['user_msgs']} msgs  │  🔢 {conv['steps']} steps{files_tag}")
        print(f"        ID: {conv['id']}")
        # Show clean first message
        msg = conv["first_msg"][:90]
        print(f"        💬 {msg}")
        # Show last user message if different
        last = conv["last_user_msg"]
        if last and last[:60] != msg[:60]:
            print(f"        ↳  {last[:90]}")
        # Show files if any
        if conv["files_written"]:
            for fp in conv["files_written"][:2]:
                short = fp.split("/")[-1]
                print(f"           📄 {short}")
        print()

    print("─" * 72)
    print()
    print("  To resume, type to the agent:")
    print("    \"resume conversation [ID]\"")
    print("    \"resume [first 8 chars of ID]\"")
    print()
    print("  Or in terminal:")
    print("    agy-history resume <ID>")
    print()
    print(f"  Showing {len(conversations)} conversation(s).", end="")
    if args.search:
        print(f"  (filter: '{args.search}')", end="")
    print()
    print()


if __name__ == "__main__":
    main()
