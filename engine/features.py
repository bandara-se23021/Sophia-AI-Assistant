import os
import re
import sqlite3
import webbrowser
from contextlib import closing
from pathlib import Path


from engine.command import speak
from playsound import playsound
import eel
from engine.config import ASSISTANT_NAME
from engine.db import DATABASE_PATH as kit


# Sound function for playing sound
def playAssistantSound():
    music_path = Path(__file__).resolve().parent.parent / "www" / "assets" / "audio" / "start_sound.mp3"
    playsound(str(music_path))

@eel.expose
#Click sound for mic button
def playClickSound():
    music_path = Path(__file__).resolve().parent.parent / "www" / "assets" / "audio" / "click_sound.mp3"
    playsound(str(music_path))

def openCommand(query):
    command = query.casefold()
    command = re.sub(rf"\b{re.escape(ASSISTANT_NAME.casefold())}\b", "", command)
    open_match = re.search(r"\bopen\b\s*(.*)$", command)
    if open_match:
        command = open_match.group(1)
    command = command.strip(" ,")

    if not command:
        speak("What would you like me to open?")
        return

    with closing(sqlite3.connect(kit)) as connection:
        application = connection.execute(
            "SELECT path FROM sys_command WHERE LOWER(name) = ?",
            (command,),
        ).fetchone()
        website = None
        if application is None:
            website = connection.execute(
                "SELECT url FROM web_command WHERE LOWER(name) = ?",
                (command,),
            ).fetchone()

    if application is not None:
        try:
            os.startfile(application[0])
        except OSError as error:
            print(f"Could not open {command}: {error}")
            speak(f"I couldn't open {command}.")
            return
    elif website is not None:
        webbrowser.open(website[0])
    else:
        try:
            os.startfile(command)
        except OSError as error:
            print(f"Could not open {command}: {error}")
            speak(f"I couldn't find {command}.")
            return

    speak("Opening " + command)


def PlayYoutube(query):
    query = query.lower()
    search_term = extract_yt_term(query)
    if search_term:
        speak("Playing " + search_term + " on YouTube")
        try:
            import pywhatkit

            pywhatkit.playonyt(search_term)
        except Exception as error:
            print(f"YouTube request failed: {error}")
            speak("I couldn't connect to YouTube. Please check your internet connection.")

    else:
        speak("Sorry, I couldn't find what to play on YouTube")


def extract_yt_term(command):
    command = command.lower()
    pattern = r'play\s+(.*?)\s+on\s+youtube'
    match = re.search(pattern, command, re.IGNORECASE)
    return match.group(1) if match else None