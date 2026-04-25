import os, webbrowser

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def clean_query(command):
    query = command.replace("play", "").strip()
    query = query.replace("on spotify", "").replace("spotify", "")
    return query.strip()

def find_file(name):
    search_roots = [
        os.path.expanduser("~/Desktop"),
        os.path.expanduser("~/Documents"),
        os.path.expanduser("~/Downloads"),
        os.path.expanduser("~/Pictures"),
        os.path.expanduser("~/Music"),
    ]
    name = name.lower()
    found = []
    for root in search_roots:
        for dirpath, _, files in os.walk(root):
            for f in files:
                if name in f.lower():
                    found.append(os.path.join(dirpath, f))
            if len(found) >= 5:
                break
    if found:
        return "Here's what I found:\n" + "\n".join(found[:5])
    return f"Couldn't find anything matching '{name}'. Try a different name?"

def system_info(query):
    try:
        import psutil
        cpu  = psutil.cpu_percent(interval=0.5)
        ram  = psutil.virtual_memory().percent
        bat  = psutil.sensors_battery()
        bat_str = f"{int(bat.percent)}%" if bat else "not detected"

        if "cpu" in query:
            load = "running smoothly" if cpu < 50 else "working pretty hard"
            return f"Your CPU is {load} at {cpu}% usage."
        elif "ram" in query or "memory" in query:
            load = "looking good" if ram < 70 else "running a bit tight"
            return f"RAM is {load} — {ram}% in use."
        elif "battery" in query or "bat" in query:
            if bat:
                status = "charging" if bat.power_plugged else "on battery"
                return f"Battery is at {int(bat.percent)}% and {status}."
            return "Couldn't detect a battery on this machine."
        else:
            return f"System check — CPU: {cpu}% | RAM: {ram}% | Battery: {bat_str}"
    except ImportError:
        return "psutil isn't installed. Run: pip install psutil"

# ─────────────────────────────────────────────
#  PARSER
# ─────────────────────────────────────────────
def parse_command(command: str):
    c = command.lower().strip()

    if "time" in c and not c.startswith("play"):
        return ("time", c)
    if c.startswith("find ") or c.startswith("search file "):
        return ("find", c)
    if any(c.startswith(k) for k in ["system info", "cpu", "ram", "battery", "memory"]):
        return ("sysinfo", c)
    if c.startswith("play"):
        return ("play_spotify" if "spotify" in c else "play_youtube", c)
    if c.startswith("open"):
        return ("open", c.replace("open", "", 1).strip())
    if c.startswith("search") or c.startswith("what is"):
        return ("search", c)

    return ("unknown", c)

# ─────────────────────────────────────────────
#  MEDIA HANDLERS
# ─────────────────────────────────────────────
def play_spotify(command):
    query = clean_query(command)
    webbrowser.open(f"https://open.spotify.com/search/{query}")
    return f"Pulling up '{query}' on Spotify for you..."

def play_youtube(command):
    query = clean_query(command)
    webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
    return f"Loading '{query}' on YouTube..."

def open_spotify():
    paths = [
        r"C:\Users\%USERNAME%\AppData\Roaming\Spotify\Spotify.exe",
        r"C:\Program Files\Spotify\Spotify.exe"
    ]
    for p in paths:
        p = os.path.expandvars(p)
        if os.path.exists(p):
            os.startfile(p)
            return "Launching Spotify — enjoy the music."
    webbrowser.open("https://open.spotify.com")
    return "Couldn't find the Spotify app, so I opened it in your browser."

def open_folder(name):
    folders = {
        "downloads": os.path.expanduser("~/Downloads"),
        "documents": os.path.expanduser("~/Documents"),
        "desktop":   os.path.expanduser("~/Desktop")
    }
    if name in folders:
        os.startfile(folders[name])
        return f"Opening your {name.capitalize()} folder..."
    return "Hmm, I don't know that folder. Try: downloads, documents, or desktop."

def open_app(target):
    import subprocess, time

    known_apps = {
        "chrome":   r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "notepad":  "notepad.exe",
        "explorer": "explorer.exe",
        "calc":     "calc.exe",
        "vscode":   r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    }

    if target == "spotify":
        return open_spotify()

    if target in known_apps:
        path = os.path.expandvars(known_apps[target])
        try:
            subprocess.Popen(path)
            return f"Launching {target.capitalize()}..."
        except Exception:
            pass

    try:
        import pyautogui
        pyautogui.press("win")
        time.sleep(0.8)
        pyautogui.write(target, interval=0.05)
        time.sleep(0.8)
        pyautogui.press("enter")
        return f"Couldn't find a direct path, so I searched Windows for '{target}'."
    except ImportError:
        return "pyautogui isn't installed. Run: pip install pyautogui"
    except Exception as e:
        return f"Something went wrong trying to open '{target}': {str(e)}"

def search_web(raw):
    query = raw.replace("search", "", 1).replace("what is", "", 1).strip()
    webbrowser.open(f"https://www.google.com/search?q={query}")
    return f"Searching Google for '{query}'..."

# ─────────────────────────────────────────────
#  ROUTER
# ─────────────────────────────────────────────
# ─────────────────────────────────────────────
#  ROUTER
# ─────────────────────────────────────────────
def handle_command(command):
    from datetime import datetime
    c = command.lower().strip()

    # ── CHAINED COMMANDS ──
    if "start coding" in c or "work mode" in c:
        open_app("vscode")
        search_web("python documentation")
        # Kept this from your original file since it's useful
        open_folder("documents") 
        return "Setting up your coding environment..."

    if "focus mode" in c:
        open_app("vscode")
        search_web("productivity tips")
        return "Entering focus mode..."

    if "study mode" in c:
        open_app("chrome")
        search_web("Khan Academy")
        return "Study mode activated — Chrome and Khan Academy are ready for you."

    if "music mode" in c or "chill mode" in c:
        open_spotify()
        return "Chill mode on. Spotify is launching — sit back."

    if "start meeting" in c or "meeting mode" in c:
        open_app("chrome")
        search_web("Google Meet")
        return "Meeting mode on — Google Meet is loading in Chrome."

    # ── STANDARD INTENT PARSING ──
    intent, raw = parse_command(command)

    if intent == "time":
        return "It's " + datetime.now().strftime("%H:%M") + " right now."
    elif intent == "find":
        name = raw.replace("find", "").replace("search file", "").strip()
        return find_file(name)
    elif intent == "sysinfo":
        return system_info(raw)
    elif intent == "play_spotify":
        return play_spotify(raw)
    elif intent == "play_youtube":
        return play_youtube(raw)
    elif intent == "open":
        if raw in ["downloads", "documents", "desktop"]:
            return open_folder(raw)
        return open_app(raw)
    elif intent == "search":
        return search_web(raw)

    return "Not sure what you mean. Try: open chrome / play lofi / search python / find notes.txt / system info"