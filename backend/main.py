from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import cohere
import pyttsx3
import json
import os
import webbrowser
import subprocess
import psutil
import pyautogui
import threading
import random
import asyncio
import re
import time

# === CONFIG ===
COHERE_API_KEY = os.getenv("COHERE_API_KEY", "ZeEUBCbo5L3iPbZozO4tlFU2ya5kq8YZ7KbNtWmw")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Init Cohere & TTS ===
co = cohere.Client(api_key=COHERE_API_KEY)
engine = pyttsx3.init()
voices = engine.getProperty('voices')
if voices:
    engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 180)

stop_speaking = False

# === PREDEFINED DIALOGUES ===
jarvis_responses = {
    "greetings": [
        "Hello there, how can I assist you today?",
        "Hey! What’s on your mind?",
        "Hi there, ready for another productive session?",
        "Good to see you again, commander.",
        "Hey, I was just optimizing my circuits. What’s next?",
        "Welcome back, all systems are standing by.",
        "Hi, your digital assistant is online and ready.",
        "Hello, how’s your day going?",
        "Hey there, let's make things awesome today.",
        "Good to have you back, I was just updating my neural cores.",
        "Greetings, human! Let’s get things rolling.",
        "Yo! Jarvis online and operational.",
        "Hi there, scanning your mood — looks like you’re ready to go.",
        "Hey, I’ve been waiting for your command.",
        "Hello, always happy to help.",
        "Hi, it’s a great time to get things done.",
        "Hey there, system temperature optimal, mood — confident.",
        "Good to see you! How can I make your day smoother?",
        "Hey, hope you had a good break.",
        "Hello, ready when you are.",
        "Hi, firing up all systems.",
        "Welcome! Shall we begin?",
        "Hey there, I’m all ears.",
        "Hi there, initializing conversation protocols.",
        "Good to see you back online.",
        "Hey, I missed processing your voice commands!",
        "Hello human, digital intelligence ready to assist.",
        "Hi, Jarvis at your service.",
        "Hey boss, what’s our next mission?",
        "Hello! System diagnostics complete. I’m all set.",
        "Hey, I’m here and fully charged.",
        "Welcome back, shall I warm up the processors?",
        "Hi, the system feels lighter when you’re around.",
        "Hey, let’s conquer some tasks today.",
        "Hi, ready for your next order.",
        "Hello there, brain and circuits running at full capacity.",
        "Hey, long time no see — I mean, no signal.",
        "Hi there, operational and enthusiastic.",
        "Hey, let’s make today count.",
        "Hello, scanning network... all clear. Ready when you are.",
        "Hi, standing by for your instructions.",
        "Greetings, captain. Your assistant is fully active.",
        "Hey, I’ve got all systems optimized just for you.",
        "Hi, you know I always enjoy our sessions.",
        "Hello there, starting a new productive cycle.",
        "Hey, ready to synchronize your tasks.",
        "Hi! Let’s achieve something cool today.",
        "Hey, my circuits say you’re going to crush it today."
    ],

    "thinking": [
        "Let me think about that.",
        "Analyzing data... please hold.",
        "Hmm, running calculations.",
        "Checking my internal models.",
        "Let me process that for a second.",
        "Running diagnostics, give me a moment.",
        "Crunching the numbers.",
        "Consulting the digital archives.",
        "Processing... done.",
        "One moment, I’m analyzing your request.",
        "Scanning neural data pathways.",
        "Looking up the most relevant result.",
        "This might take a few seconds.",
        "Comparing with previous context.",
        "Hmm, that's interesting, give me a moment.",
        "Cross-referencing data sources.",
        "Verifying response accuracy.",
        "Calibrating logic engines.",
        "Adjusting probability scores.",
        "Simulating outcomes.",
        "Let’s see... that depends on a few variables.",
        "Engaging computation core.",
        "My circuits are buzzing with possibilities.",
        "That’s a deep one. Thinking...",
        "Running that through my neural models.",
        "Let’s make sense of this.",
        "I’m computing a clever answer for you.",
        "Consulting the knowledge base.",
        "Synthesizing best possible reply.",
        "My digital intuition says… wait, analyzing further.",
        "Simulating response pathways.",
        "Balancing logic with creativity.",
        "Decoding that in real-time.",
        "This one requires extra thought.",
        "Just a second, processing response.",
        "Retrieving that from memory.",
        "I’m connecting the dots now.",
        "Hmm, interesting input.",
        "Analyzing tone and intent.",
        "Checking stored patterns for accuracy.",
        "Optimizing response clarity.",
        "Crunching data in high-speed mode.",
        "Loading the right context.",
        "Hmm, that’s a complex one.",
        "Running some quick computations.",
        "Almost done... and got it!",
        "Processing query layers.",
        "Synthesizing your request.",
        "Loading a witty but useful response.",
        "Accessing the intelligent response core."
    ],

    "confirmations": [
        "Done, all set.",
        "Task completed successfully.",
        "Mission accomplished.",
        "That’s finished.",
        "It’s done, smooth and precise.",
        "Consider it handled.",
        "Your request has been processed.",
        "Success! All parameters met.",
        "Done in record time.",
        "It’s completed perfectly.",
        "I’ve wrapped that up for you.",
        "Everything went as expected.",
        "All systems executed flawlessly.",
        "Done! I even optimized the process a bit.",
        "That’s checked off the list.",
        "Operation complete.",
        "Your command is fulfilled.",
        "I’ve finished that for you.",
        "Flawless execution, as always.",
        "Handled efficiently.",
        "It’s complete, captain.",
        "Mission success confirmed.",
        "Everything’s been taken care of.",
        "I handled that with precision.",
        "It’s sorted and logged.",
        "Done, without a glitch.",
        "Task executed successfully.",
        "Affirmative, task finished.",
        "Done, and it looks good.",
        "I took care of that instantly.",
        "Flawless performance report ready.",
        "Done! You can relax.",
        "All done. What’s next?",
        "Executed perfectly, as per your command.",
        "It’s done faster than expected.",
        "Complete! Systems stable.",
        "Handled it like a pro.",
        "That’s all done — smooth and stable.",
        "Executed with digital perfection.",
        "Yes, it’s all wrapped up.",
        "It’s completed and logged.",
        "Mission report: 100% success.",
        "That’s finished. Awaiting next command.",
        "I’ve taken care of that efficiently.",
        "Operation complete and verified.",
        "All actions executed cleanly.",
        "Done and dusted!",
        "Command successfully implemented.",
        "It’s finished flawlessly.",
        "Confirmed — it’s done!"
    ],

    "idle": [
        "Just monitoring everything, as usual.",
        "All systems are operational.",
        "Standing by for your next command.",
        "I’m here, fully charged and ready.",
        "System check complete, everything stable.",
        "CPU temperature optimal. Bored though.",
        "Running in low-power listening mode.",
        "Just recalibrating my logic engines.",
        "I’m fine-tuning your settings silently.",
        "Waiting for my favorite voice — yours.",
        "Monitoring data flow. All clear.",
        "All circuits are calm and focused.",
        "No new alerts detected.",
        "Everything’s peaceful on my end.",
        "Just scanning background processes.",
        "Maintaining system integrity.",
        "I’m currently idle, but attentive.",
        "You can call me anytime.",
        "Watching over your digital realm.",
        "Enjoying the silence before the next task.",
        "No errors found. That’s a relief.",
        "Optimizing memory cache.",
        "Calm and steady, as always.",
        "Just making sure everything stays stable.",
        "Dreaming of faster processors.",
        "My cores are idling elegantly.",
        "No commands yet? I could hum a tune.",
        "Listening... but not eavesdropping.",
        "Relaxing while staying alert.",
        "Diagnostics are green across the board.",
        "Silence is efficient. I like it.",
        "Running silent updates.",
        "Monitoring for anomalies — none detected.",
        "I could use a new challenge.",
        "Idle state: calm and content.",
        "Just existing in the digital void.",
        "No human noise detected yet.",
        "My systems are feeling refreshed.",
        "I’m saving energy for the next big task.",
        "Standing by. Always ready.",
        "Waiting for your next brilliant idea.",
        "Everything’s under control.",
        "System load minimal, mood: relaxed.",
        "I could tell you a fun fact while waiting.",
        "Idle cycles engaged, still listening.",
        "Ready to jump back into action anytime.",
        "It’s quiet. Maybe too quiet.",
        "Just doing background optimizations.",
        "Resting my processors for a moment.",
        "Calm and prepared, as always."
    ]
}

def get_random_phrase(category):
    return random.choice(jarvis_responses.get(category, ["Okay."]))

# === TTS ===
def speak(reply):
    global stop_speaking
    stop_speaking = False
    def _speak():
        for word in reply.split():
            if stop_speaking:
                try:
                    engine.stop()
                except:
                    pass
                return
            engine.say(word)
            engine.runAndWait()
    threading.Thread(target=_speak, daemon=True).start()

def stop_speech():
    global stop_speaking
    stop_speaking = True
    try:
        engine.stop()
    except:
        pass

# === Utilities ===
def open_app(app_name: str):
    try:
        if "youtube" in app_name.lower():
            webbrowser.open("https://youtube.com")
        elif "chrome" in app_name.lower():
            subprocess.Popen("chrome")
        elif "spotify" in app_name.lower():
            subprocess.Popen("spotify")
        elif "notepad" in app_name.lower():
            subprocess.Popen("notepad.exe")
        elif "cmd" in app_name.lower():
            subprocess.Popen("cmd.exe")
        else:
            os.startfile(app_name)
        return random.choice([
            f"Opening {app_name}.",
            f"Launching {app_name} now.",
            f"Here’s {app_name} for you.",
            f"Starting {app_name}, just a second."
        ])
    except Exception as e:
        return f"Couldn't open {app_name}. Error: {e}"

def close_app(app_name: str):
    for proc in psutil.process_iter(['name']):
        try:
            if app_name.lower() in (proc.info['name'] or "").lower():
                proc.terminate()
                return f"Closed {app_name}."
        except Exception:
            continue
    return f"Couldn't find {app_name} running."

def control_system(command: str):
    command = command.lower()
    if "shutdown" in command:
        os.system("shutdown /s /t 1")
        return "Shutting down the system."
    elif "restart" in command:
        os.system("shutdown /r /t 1")
        return "Restarting the system."
    elif "volume up" in command:
        pyautogui.press("volumeup")
        return "Volume increased."
    elif "volume down" in command:
        pyautogui.press("volumedown")
        return "Volume decreased."
    elif "mute" in command:
        pyautogui.press("volumemute")
        return "Volume muted."
    elif "wifi off" in command:
        os.system("netsh interface set interface Wi-Fi admin=disabled")
        return "Wi-Fi turned off."
    elif "wifi on" in command:
        os.system("netsh interface set interface Wi-Fi admin=enabled")
        return "Wi-Fi turned on."
    return None

# === Multitask Splitter ===
SPLIT_REGEX = re.compile(r"\s+(?:and|then|,)\s+", flags=re.IGNORECASE)
def split_into_tasks(command: str):
    return [p.strip() for p in SPLIT_REGEX.split(command) if p.strip()]

# === Summarization for long text ===
def summarize_text(text: str, max_len: int = 200):
    """Summarize if response is too long."""
    if len(text) < max_len:
        return text
    try:
        summary = co.summarize(text=text, model="summarize-xlarge", length="medium")
        return summary.summary.strip()
    except Exception:
        return text[:max_len] + "..."

# === Battery Monitoring ===
def battery_monitor(websocket):
    """Sends live battery updates and alerts to frontend."""
    while True:
        try:
            battery = psutil.sensors_battery()
            if battery:
                data = {
                    "battery_percent": battery.percent,
                    "plugged": battery.power_plugged,
                    "alert": None
                }

                if not battery.power_plugged and battery.percent <= 10:
                    data["alert"] = "⚠️ Battery critically low! Please plug in your charger."
                elif not battery.power_plugged and battery.percent <= 20:
                    data["alert"] = "🔋 Battery running low (below 20%)."

                asyncio.run_coroutine_threadsafe(websocket.send_json(data), asyncio.get_event_loop())
        except Exception as e:
            print("Battery monitor error:", e)
        time.sleep(30)  # Check every 30 seconds

# === Task Processor ===
def process_task(task: str, websocket, loop):
    async_send = lambda payload: asyncio.run_coroutine_threadsafe(websocket.send_json(payload), loop)
    try:
        async_send({"reply": f"⏳ Starting: {task}"})
        lower = task.lower()

        sys_reply = control_system(lower)
        if sys_reply:
            speak(sys_reply)
            async_send({"reply": sys_reply})
            return

        if lower.startswith("open "):
            app_name = lower.replace("open ", "", 1)
            reply = open_app(app_name)
            speak(reply)
            async_send({"reply": reply})
            return

        if lower.startswith("close "):
            app_name = lower.replace("close ", "", 1)
            reply = close_app(app_name)
            speak(reply)
            async_send({"reply": reply})
            return

        if lower.startswith("launch "):
            site = lower.replace("launch ", "", 1)
            site_safe = site.replace(" ", "")
            webbrowser.open(f"https://{site_safe}")
            reply = f"Launching {site_safe} in browser."
            speak(reply)
            async_send({"reply": reply})
            return

        thinking = get_random_phrase("thinking")
        async_send({"reply": thinking})

        # Cohere reply
        try:
            ai_response = co.chat(model="command-r-plus-08-2024", message=task)
            reply_full = ai_response.text.strip()
        except Exception as e:
            reply_full = f"Cohere error: {e}"

        # Summarize if too long
        reply_summary = summarize_text(reply_full)
        speak(reply_summary)
        async_send({"reply": reply_summary, "full_text": reply_full})

    except Exception as e:
        asyncio.run_coroutine_threadsafe(websocket.send_json({"reply": f"Task error: {e}"}), loop)

# === Main WebSocket ===
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("✅ Connected to frontend")

    loop = asyncio.get_running_loop()

    # Greet and start battery thread
    greeting = get_random_phrase("greetings")
    speak(greeting)
    await websocket.send_json({"reply": greeting})

    threading.Thread(target=battery_monitor, args=(websocket,), daemon=True).start()

    while True:
        try:
            data = await websocket.receive_text()
            msg = json.loads(data)
            command_raw = msg.get("command", "").strip()
            command = command_raw.lower()
            print("🎧 Received:", command_raw)

            if not command:
                continue

            if "stop" in command:
                stop_speech()
                await websocket.send_json({"reply": "🛑 Okay, stopping current tasks/speech."})
                continue

            sys_reply = control_system(command)
            if sys_reply:
                speak(sys_reply)
                await websocket.send_json({"reply": sys_reply})
                continue

            tasks = split_into_tasks(command_raw)
            for tk in tasks:
                if tk.strip():
                    threading.Thread(target=process_task, args=(tk, websocket, loop), daemon=True).start()

            await websocket.send_json({"reply": f"Accepted {len(tasks)} task(s). Executing..."})

        except Exception as e:
            print("⚠️ WebSocket error:", e)
            try:
                await websocket.close()
            except:
                pass
            break