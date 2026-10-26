
import threading
import webbrowser
from pathlib import Path

import eel

import engine.command
import engine.productivity
from engine.db import initialize_database
from engine.features import playAssistantSound


PROJECT_ROOT = Path(__file__).resolve().parent
initialize_database()

eel.init(str(PROJECT_ROOT / 'www'))

playAssistantSound()

threading.Timer(1, webbrowser.open, args=['http://localhost:8000/index.html']).start()

eel.start('index.html', mode=None, host='localhost', block=True)
