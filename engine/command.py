import re
import threading
import pyttsx3
import speech_recognition as sr
import eel


_conversation_state = None
_conversation_lock = threading.Lock()
_spoken_digits = {
    "zero": "0",
    "oh": "0",
    "o": "0",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
}
_spoken_tens = {
    "twenty": "2",
    "thirty": "3",
    "forty": "4",
    "fifty": "5",
    "sixty": "6",
    "seventy": "7",
    "eighty": "8",
    "ninety": "9",
}
_spoken_teens = {
    "ten": "10",
    "eleven": "11",
    "twelve": "12",
    "thirteen": "13",
    "fourteen": "14",
    "fifteen": "15",
    "sixteen": "16",
    "seventeen": "17",
    "eighteen": "18",
    "nineteen": "19",
}
_phone_number_fillers = {"my", "phone", "number", "is", "the", "please"}


def speak(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    if len(voices) > 1:
        engine.setProperty('voice', voices[1].id)
    engine.setProperty('rate', 170)
    eel.DisplayMessage(text)
    engine.say(text)
    engine.runAndWait()

@eel.expose
def takeCommand():
    r = sr.Recognizer()
    with _conversation_lock:
        conversation = _conversation_state
    phrase_time_limit = 30 if conversation and conversation["step"] in {"content", "message"} else 15
    try:
        with sr.Microphone() as source:
            print("Listening...")
            eel.DisplayMessage('Listening...')
            r.pause_threshold = 1
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source, timeout=10, phrase_time_limit=phrase_time_limit)

        print("Recognizing...")
        eel.DisplayMessage('Recognizing...')
        query = r.recognize_google(audio, language='en')
        print(f"User said: {query}")
        eel.DisplayMessage(query)
    except sr.WaitTimeoutError:
        eel.DisplayMessage("I didn't hear anything. Please try again.")
        return ""
    except sr.UnknownValueError:
        eel.DisplayMessage("I couldn't understand that. Please try again.")
        return ""
    except sr.RequestError as error:
        print(f"Speech recognition service error: {error}")
        eel.DisplayMessage("Speech recognition is unavailable.")
        return ""
    except OSError as error:
        print(f"Microphone error: {error}")
        eel.DisplayMessage("The microphone is unavailable.")
        return ""
    return query.lower()


@eel.expose
def allCommands():
    try:
        query = takeCommand()
        print(query)
        if query:
            return processTextCommand(query)
        with _conversation_lock:
            conversation_active = _conversation_state is not None
        if conversation_active:
            prompt = "I didn't catch that. Please say your answer again."
            speak(prompt)
            return {"message": prompt, "conversation": True}
    except Exception as error:
        print(f"Command error: {error}")
        eel.DisplayMessage("I couldn't complete that command.")
    finally:
        with _conversation_lock:
            conversation_active = _conversation_state is not None
        if not conversation_active:
            eel.ShowHood()


@eel.expose
def processTextCommand(query):
    from engine.features import PlayYoutube, openCommand
    from engine.productivity import create_word_document, draft_email

    if not isinstance(query, str):
        return {"message": "Please say or type your answer again."}

    normalized_query = query.strip()
    if not normalized_query:
        return {"message": "Type a command first."}
    intent_query = normalized_query.rstrip(" \t\r\n.!?,")

    global _conversation_state
    with _conversation_lock:
        conversation = _conversation_state

    if conversation is not None:
        return _continue_conversation(normalized_query, conversation)

    greeting_query = re.sub(r"[^\w\s]", " ", intent_query)
    greeting_query = re.sub(r"\s+", " ", greeting_query).strip()
    whatsapp_intent = re.sub(
        r"\b(?:what's\s*app|what\s+is\s+app)\b",
        "whatsapp",
        intent_query,
        flags=re.IGNORECASE,
    )
    whatsapp_intent = re.sub(r"\s+", " ", whatsapp_intent).strip()

    if re.fullmatch(
        r"(?:hi|hello|hey|good morning|good afternoon|good evening)\s+(?:sophia|sofia)",
        greeting_query,
        re.IGNORECASE,
    ):
        response = "Hello! How can I help you?"
        speak(response)
        return {"message": response}

    whatsapp_match = re.fullmatch(
        r"send\s+(?:a\s+)?whatsapp\s+message\s+to\s+(\+?\d[\d\s().-]*)\s+"
        r"(?:saying|that says)\s+(.+)",
        normalized_query,
        re.IGNORECASE,
    )
    if whatsapp_match:
        phone_number, message = whatsapp_match.groups()
        if not re.fullmatch(r"\+[1-9]\d{7,14}", re.sub(r"[\s().-]", "", phone_number)):
            response = "Use an international phone number, such as +94771234567."
            speak(response)
            return {"message": response}
        speak(f"I prepared your WhatsApp message to {phone_number}. Please confirm it on screen to send.")
        return {
            "action": "confirm_whatsapp",
            "phone_number": phone_number,
            "message": message.strip(),
        }

    word_match = re.fullmatch(
        r"(?:create|write|make)\s+(?:a\s+)?(?:word\s+)?document\s+"
        r"(?:titled|called)\s+(.+?)\s+(?:with content|containing)\s+(.+)",
        intent_query,
        re.IGNORECASE | re.DOTALL,
    )
    if word_match:
        title, content = word_match.groups()
        speak(f"Opening your unsaved document, {title}, in Microsoft Word.")
        try:
            response = create_word_document(title, content)
        except (OSError, RuntimeError, ValueError) as error:
            response = str(error)
            speak(response)
            return {"message": response}
        speak(response)
        return {"message": response}

    email_match = re.fullmatch(
        r"(?:write|draft|compose)\s+(?:an?\s+)?email\s+to\s+(\S+)\s+"
        r"(?:with\s+)?subject\s+(.+?)\s+(?:and\s+)?(?:message|body)\s+(.+)",
        normalized_query,
        re.IGNORECASE | re.DOTALL,
    )
    if email_match:
        recipient, subject, body = email_match.groups()
        try:
            message = draft_email(recipient, subject, body)
        except (OSError, RuntimeError, ValueError) as error:
            message = f"Could not open the email draft: {error}"
            speak(message)
            return {"message": message}
        speak(message)
        return {"message": message}

    if re.fullmatch(
        r"(?:(?:can|could|would)\s+you\s+)?(?:please\s+)?"
        r"(?:(?:i\s+(?:want|need|would like)\s+to|i'd like to)\s+)?"
        r"(?:write|draft|compose|prepare|create|send|start)\s+"
        r"(?:an?\s+)?(?:email|email draft)",
        intent_query,
        re.IGNORECASE,
    ):
        return _start_conversation(
            {"kind": "email", "step": "recipient"},
            "Sure. What email address should I use? Say it clearly, for example, name at example dot com.",
        )

    if re.fullmatch(
        r"(?:(?:can|could|would)\s+you\s+)?(?:please\s+)?"
        r"(?:i\s+(?:want|need)\s+to\s+)?(?:create|write|make|open|start)\s+"
        r"(?:for\s+me\s+)?(?:a\s+)?(?:(?:new|unsaved)\s+)?"
        r"(?:word\s+)?document(?:\s+for\s+me)?",
        intent_query,
        re.IGNORECASE,
    ):
        return _start_conversation(
            {"kind": "word", "step": "title"},
            "What title would you like for your Word document?",
        )

    if re.fullmatch(
        r"(?:(?:i\s+(?:want|need|would like)\s+to|i'd like to|can you|could you)\s+)?"
        r"(?:please\s+)?send\s+(?:a\s+)?(?:whatsapp\s+)?message"
        r"(?:\s+(?:on|via)\s+whatsapp)?",
        whatsapp_intent,
        re.IGNORECASE,
    ):
        return _start_conversation(
            {"kind": "whatsapp", "step": "phone"},
            "Who should I send the WhatsApp message to? Say the international phone number one digit at a time. For example, plus, 9, 4, 7, 7, 1, 2, 3, 4, 5, 6, 7.",
        )

    if re.search(r"\bopen\b", normalized_query, re.IGNORECASE):
        openCommand(normalized_query)
        return {"message": f"Opening request: {normalized_query}"}

    if "on youtube" in normalized_query.casefold():
        PlayYoutube(normalized_query)
        return {"message": f"YouTube request: {normalized_query}"}

    response = (
        "I can open apps, play YouTube videos, send WhatsApp messages, create Word documents, and draft emails"
    )
    speak(response)
    return {"message": response}


def _start_conversation(state, prompt):
    global _conversation_state
    with _conversation_lock:
        _conversation_state = state
    speak(prompt)
    return {"message": prompt, "conversation": True}


def _finish_conversation():
    global _conversation_state
    with _conversation_lock:
        _conversation_state = None


def _normalize_spoken_phone_number(value):
    tokens = re.findall(r"\+|[a-zA-Z]+|\d+", value.casefold())
    normalized = ""
    pending_tens = False
    for token in tokens:
        if token in {"+", "plus"}:
            if normalized:
                return ""
            normalized = "+"
        elif token.isdigit():
            normalized += token
            pending_tens = False
        elif token in _spoken_digits:
            normalized += _spoken_digits[token]
            pending_tens = False
        elif token in _spoken_tens:
            if pending_tens:
                normalized += "0"
            normalized += _spoken_tens[token]
            pending_tens = True
        elif token in _spoken_teens:
            if pending_tens:
                normalized += "0"
            normalized += _spoken_teens[token]
            pending_tens = False
        elif token in _phone_number_fillers:
            continue
        else:
            return ""

    if pending_tens:
        normalized += "0"
    if not normalized.startswith("+") and re.fullmatch(r"[1-9]\d{7,14}", normalized):
        normalized = "+" + normalized
    return normalized


def _normalize_spoken_email(value):
    normalized = value.casefold().strip()
    normalized = re.sub(r"\s+at\s+", "@", normalized)
    normalized = re.sub(r"\s+dot\s+", ".", normalized)
    return re.sub(r"\s+", "", normalized)


def _continue_conversation(answer, state):
    from engine.productivity import create_word_document, draft_email, sendWhatsAppMessage

    normalized_answer = answer.strip()
    lowered_answer = normalized_answer.casefold().rstrip(" .,!?:;")
    if lowered_answer in {"cancel", "stop", "never mind", "nevermind"} or (
        state["kind"] == "whatsapp" and lowered_answer in {"no", "no thanks"}
    ):
        _finish_conversation()
        speak("Okay, I canceled that.")
        return {"message": "Conversation canceled."}

    if state["kind"] == "word" and state["step"] == "title":
        state["title"] = normalized_answer
        state["step"] = "content"
        prompt = "What would you like me to write in the document? Say the content now."
        speak(prompt)
        return {"message": prompt, "conversation": True}

    if state["kind"] == "word" and state["step"] == "content":
        _finish_conversation()
        speak(f"Opening your unsaved document, {state['title']}, in Microsoft Word.")
        try:
            result = create_word_document(state["title"], normalized_answer)
        except (OSError, RuntimeError, ValueError) as error:
            message = f"I couldn't create the Word document: {error}"
            speak(message)
            return {"message": message}
        speak(result)
        return {"message": result}

    if state["kind"] == "email" and state["step"] == "recipient":
        recipient = _normalize_spoken_email(normalized_answer)
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", recipient):
            prompt = "I couldn't recognize that email address. Please say it again, using at and dot if needed."
            speak(prompt)
            return {"message": prompt, "conversation": True}
        state["recipient"] = recipient
        state["step"] = "subject"
        prompt = "What subject would you like for the email?"
        speak(prompt)
        return {"message": prompt, "conversation": True}

    if state["kind"] == "email" and state["step"] == "subject":
        state["subject"] = normalized_answer
        state["step"] = "message"
        prompt = "What would you like the email to say?"
        speak(prompt)
        return {"message": prompt, "conversation": True}

    if state["kind"] == "email" and state["step"] == "message":
        _finish_conversation()
        try:
            result = draft_email(state["recipient"], state["subject"], normalized_answer)
        except (OSError, RuntimeError, ValueError) as error:
            message = f"Could not open the email draft: {error}"
            speak(message)
            return {"message": message}
        speak(result)
        return {"message": result}

    if state["kind"] == "whatsapp" and state["step"] == "phone":
        phone_number = _normalize_spoken_phone_number(normalized_answer)
        if not re.fullmatch(r"\+[1-9]\d{7,14}", phone_number):
            prompt = "I couldn't recognize that number. Please say the country code followed by each digit separately, such as 9, 4, 7, 7, 1, 2, 3, 4, 5, 6, 7."
            speak(prompt)
            return {"message": prompt, "conversation": True}
        state["phone_number"] = phone_number
        state["step"] = "message"
        prompt = "What message would you like me to send?"
        speak(prompt)
        return {"message": prompt, "conversation": True}

    if state["kind"] == "whatsapp" and state["step"] == "message":
        state["message"] = normalized_answer
        state["step"] = "confirm"
        prompt = (
            f"I will send this to {state['phone_number']}: "
            f"{state['message']}. Should I send it? Say yes or no."
        )
        speak(prompt)
        return {"message": prompt, "conversation": True}

    if state["kind"] == "whatsapp" and state["step"] == "confirm":
        confirmation = re.sub(r"[^a-z\s]", "", lowered_answer)
        if re.fullmatch(
            r"(?:yes|yeah|yep|yes please|yes send it|send it|confirm)",
            confirmation,
        ):
            _finish_conversation()
            return {
                "action": "confirm_whatsapp",
                "phone_number": state["phone_number"],
                "message": state["message"],
                "voice_confirmed": True,
            }
        if re.fullmatch(
            r"(?:no|no thanks|no cancel|no do not send|don't send)",
            confirmation,
        ):
            _finish_conversation()
            speak("Okay, I did not send the WhatsApp message.")
            return {"message": "WhatsApp message canceled."}

        prompt = "Please say yes to send the message, no to cancel, or cancel to stop."
        speak(prompt)
        return {"message": prompt, "conversation": True}

    _finish_conversation()
    message = "That conversation could not continue. Please start again."
    speak(message)
    return {"message": message}