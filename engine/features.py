import os
import re
import sys


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from engine.command import speak
from playsound import playsound
import eel
from engine.config import ASSISTANT_NAME
import pywhatkit as kit


# Sound function for playing sound
def playAssistantSound():
    music_dir="www\\assets\\audio\\start_sound.mp3"
    playsound(music_dir)

@eel.expose
#Click sound for mic button
def playClickSound():
    music_dir="www\\assets\\audio\\click_sound.mp3"
    playsound(music_dir)

def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "")
    query = query.replace("open", "")
    query.lower()

    if query != "":
        speak("Opening" + query)
        os.system("start " + query)

    else:
        speak("{query} not found")


def PlayYoutube(query):
    query = query.lower()
    search_term = extract_yt_term(query)
    if search_term:
        speak("Playing " + search_term + "on YouTube")
        kit.playonyt(search_term)

    else:
        speak("Sorry, I couldn't find what to play on YouTube")


def extract_yt_term(command):
    command = command.lower()
    pattern = r'play\s+(.*?)\s+on\s+youtube'
    match = re.search(pattern, command, re.IGNORECASE)
    return match.group(1) if match else None