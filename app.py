from flask import Flask, request, jsonify, send_from_directory
from commands import handle_command
from memory import add_message, get_messages, load_memory, new_conv_id

app = Flask(__name__, static_folder=".")

@app.route("/")
def index():
    return send_from_directory(".", "index.html")

@app.route("/command", methods=["POST"])
def command():
    data = request.json
    user_input = data.get("command", "").strip()
    conv_id    = data.get("conv_id", new_conv_id())
    if not user_input:
        return jsonify({"response": "Say something.", "conv_id": conv_id})
    add_message(conv_id, "user", user_input)
    try:
        result = handle_command(user_input)
    except Exception as e:
        result = f"Error: {str(e)}"
    add_message(conv_id, "aria", result)
    return jsonify({"response": result, "conv_id": conv_id})

@app.route("/get_conversation", methods=["POST"])
def get_conversation():
    conv_id = request.json.get("id", "")
    return jsonify(get_messages(conv_id))

@app.route("/get_conversations", methods=["GET"])
def get_conversations():
    convs = load_memory()
    sidebar = []
    for c in convs:
        msgs = c.get("messages", [])
        preview = msgs[0]["text"] if msgs else "Empty"
        sidebar.append({"id": c["id"], "preview": preview[:32] + ("…" if len(preview) > 32 else "")})
    return jsonify(sidebar)

if __name__ == "__main__":
    app.run(debug=True)
