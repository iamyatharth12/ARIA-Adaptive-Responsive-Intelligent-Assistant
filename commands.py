import os, webbrowser

def clean_query(command):
    query = command.replace("play", "").strip()
    query = query.replace("on spotify", "").replace("spotify", "")
    return query.strip()

def parse_command(command: str):
    command = command.lower().strip()
    if "time" in command and not command.startswith("play"):
        return ("time", command)
    if command.startswith("play"):
        if "spotify" in command:
            return ("play_spotify", command)
        return ("play_youtube", command)
    elif command.startswith("open"):
        return ("open", command.replace("open", "", 1).strip())
    elif command.startswith("search") or command.startswith("what is"):
        return ("search", command)
    return ("unknown", command)

def play_spotify(command):
    query = clean_query(command)
    webbrowser.open(f"https://open.spotify.com/search/{query}")
    return f"Playing '{query}' on Spotify"

def play_youtube(command):
    query = clean_query(command)
    webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
    return f"Playing '{query}' on YouTube"

def open_spotify():
    paths = [
        r"C:\Users\%USERNAME%\AppData\Roaming\Spotify\Spotify.exe",
        r"C:\Program Files\Spotify\Spotify.exe"
    ]
    for p in paths:
        p = os.path.expandvars(p)
        if os.path.exists(p):
            os.startfile(p)
            return "Opened Spotify App"
    webbrowser.open("https://open.spotify.com")
    return "Opened Spotify in Browser"

def open_folder(name):
    folders = {
        "downloads": os.path.expanduser("~/Downloads"),
        "documents": os.path.expanduser("~/Documents"),
        "desktop":   os.path.expanduser("~/Desktop")
    }
    if name in folders:
        os.startfile(folders[name])
        return f"Opened {name}"
    return "Folder not found"

def open_target(target):
    apps = {"chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe"}
    if target == "spotify":
        return open_spotify()
    if target in apps:
        try:
            os.startfile(apps[target])
            return f"Opened {target}"
        except:
            pass
    webbrowser.open(f"https://{target}.com")
    return f"Opened {target} in browser"

def search_web(query):
    webbrowser.open(f"https://www.google.com/search?q={query}")
    return f"Searching: {query}"

def handle_command(command):
    from datetime import datetime
    intent, raw = parse_command(command)
    if intent == "time":
        return "Current time is " + datetime.now().strftime("%H:%M")
    elif intent == "play_spotify":
        return play_spotify(raw)
    elif intent == "play_youtube":
        return play_youtube(raw)
    elif intent == "open":
        if raw in ["downloads", "documents", "desktop"]:
            return open_folder(raw)
        return open_target(raw)
    elif intent == "search":
        return search_web(raw)
    return "I didn't understand that. Try: open chrome / play lofi / search python"
