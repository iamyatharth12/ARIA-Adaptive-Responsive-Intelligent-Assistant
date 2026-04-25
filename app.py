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
            if len(found) >= 5:  # cap results
                break
    if found:
        return "Found:\n" + "\n".join(found[:5])
    return f"File not found: '{name}'"

def system_info(query):
    try:
        import psutil
        cpu  = psutil.cpu_percent(interval=0.5)
        ram  = psutil.virtual_memory().percent
        bat  = psutil.sensors_battery()
        bat_str = f"{int(bat.percent)}%" if bat else "N/A"

        if "cpu" in query:
            return f"CPU usage: {cpu}%"
        elif "ram" in query or "memory" in query:
            return f"RAM usage: {ram}%"
        elif "battery" in query or "bat" in query:
            return f"Battery: {bat_str}"
        else:
            return f"CPU: {cpu}% | RAM: {ram}% | Battery: {bat_str}"
    except ImportError:
        return "psutil not installed. Run: pip install psutil"

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
#  OPEN HANDLERS
# ─────────────────────────────────────────────
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
            return f"Opening {target}..."
        except Exception:
            pass  # fall through to Windows Search

    # fallback — Windows Search
    try:
        import pyautogui
        pyautogui.press("win")
        time.sleep(0.8)
        pyautogui.write(target, interval=0.05)
        time.sleep(0.8)
        pyautogui.press("enter")
        return f"Used Windows Search to open '{target}'"
    except ImportError:
        return "pyautogui not installed. Run: pip install pyautogui"
    except Exception as e:
        return f"Failed to open '{target}': {str(e)}"

def search_web(raw):
    query = raw.replace("search", "", 1).replace("what is", "", 1).strip()
    webbrowser.open(f"https://www.google.com/search?q={query}")
    return f"Searching for: {query}"

# ─────────────────────────────────────────────
#  ROUTER
# ─────────────────────────────────────────────
def handle_command(command):
    from datetime import datetime
    intent, raw = parse_command(command)

    if intent == "time":
        return "Current time is " + datetime.now().strftime("%H:%M")
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

    return "I didn't understand that. Try: open chrome / play lofi / search python / find notes.txt / system info"
