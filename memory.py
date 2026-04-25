import json, os, uuid

MEMORY_FILE = "memory.json"

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

def new_conv_id():
    return "conv_" + str(uuid.uuid4())[:8]

def add_message(conv_id, role, text):
    data = load_memory()
    for conv in data:
        if conv["id"] == conv_id:
            conv["messages"].append({"role": role, "text": text})
            save_memory(data)
            return
    # New convo — use first user message as title (max 30 chars)
    title = (text[:30] + "...") if len(text) > 30 else text
    data.append({"id": conv_id, "title": title, "messages": [{"role": role, "text": text}]})
    save_memory(data)

def get_messages(conv_id):
    for conv in load_memory():
        if conv["id"] == conv_id:
            return conv["messages"]
    return []

def get_title(conv_id):
    for conv in load_memory():
        if conv["id"] == conv_id:
            return conv.get("title", conv_id)
    return conv_id
