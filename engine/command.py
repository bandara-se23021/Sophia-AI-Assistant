import pyttsx3
import speech_recognition as sr

def speak(text):
		engine = pyttsx3.init()
		voices = engine.getProperty('voices')
		print(voices)
		engine.setProperty('voice', voices[1].id)
		engine.setProperty('rate', 170)
		engine.say(text)
		engine.runAndWait()

def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source, timeout=10, phrase_time_limit=6)
    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en')
        print(f"User said: {query}")
    except Exception as e:
        return ""
    return query.lower()


text = takeCommand()

speak(text)