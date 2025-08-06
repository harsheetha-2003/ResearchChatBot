# services/chat_history.py

import os
import json

CHAT_HISTORY_DIR = "data/chat_history"

def _get_history_path(doc_id):
    os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)
    return os.path.join(CHAT_HISTORY_DIR, f"{doc_id}_history.json")

def save_chat_entry(doc_id, query, answer):
    path = _get_history_path(doc_id)
    history = []

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            history = json.load(f)

    history.append({
        "query": query,
        "answer": answer
    })

    with open(path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

def load_chat_history(doc_id):
    path = _get_history_path(doc_id)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
