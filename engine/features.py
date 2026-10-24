from playsound import playsound
import eel

# Sound function for playing sound
def playAssistantSound():
    music_dir="www\\assets\\audio\\start_sound.mp3"
    playsound(music_dir)

@eel.expose
#Click sound for mic button
def playClickSound():
    music_dir="www\\assets\\audio\\click_sound.mp3"
    playsound(music_dir)