import re
import threading
import webbrowser
from email.utils import parseaddr
from urllib.parse import quote, urlencode

import eel
import pythoncom
import win32com.client

from engine.command import speak


def create_word_document(title, content):
    if not isinstance(title, str) or not isinstance(content, str):
        raise ValueError("A document title and body must be text.")
    title = title.strip()
    content = content.strip()
    if not title or not content:
        raise ValueError("A document title and body are required.")

    word = None
    document = None
    selection = None
    pythoncom.CoInitialize()
    try:
        word = win32com.client.Dispatch("Word.Application")
        word.Visible = True
        document = word.Documents.Add()
        selection = word.Selection
        selection.Style = document.Styles("Title")
        selection.TypeText(title)
        selection.TypeParagraph()
        selection.Style = document.Styles("Normal")
        for paragraph in content.splitlines():
            selection.TypeText(paragraph)
            selection.TypeParagraph()
        return "Your unsaved document is open in Microsoft Word."
    except Exception as error:
        raise RuntimeError(f"Could not open Microsoft Word: {error}") from error
    finally:
        selection = None
        document = None
        word = None
        pythoncom.CoUninitialize()


def draft_email(recipient, subject, body):
    if not all(isinstance(value, str) for value in (recipient, subject, body)):
        raise ValueError("The email recipient, subject, and message must be text.")
    recipient = recipient.strip()
    subject = subject.strip()
    body = body.strip()
    parsed_address = parseaddr(recipient)[1]
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", parsed_address):
        raise ValueError("Please provide a valid email address.")
    if not subject or not body:
        raise ValueError("An email subject and message are required.")

    mailto_url = f"mailto:{quote(parsed_address, safe='@')}?{urlencode({'subject': subject, 'body': body})}"
    if not webbrowser.open(mailto_url):
        raise RuntimeError("The default email application could not be opened.")
    return f"Email draft opened for {parsed_address}. Review it and send it from your email app."


def _send_whatsapp(phone_number, message):
    try:
        import pywhatkit

        pywhatkit.sendwhatmsg_instantly(
            phone_number,
            message,
            wait_time=15,
            tab_close=True,
            close_time=3,
        )
    except Exception as error:
        print(f"WhatsApp message failed: {error}")
        message = "WhatsApp could not send the message. Check WhatsApp Web and try again."
        eel.DisplayMessage(message)
        speak(message)
    else:
        message = "WhatsApp message sent."
        eel.DisplayMessage(message)
        speak(message)


@eel.expose
def sendWhatsAppMessage(phone_number, message, confirmed=False):
    if not isinstance(phone_number, str) or not isinstance(message, str):
        raise ValueError("A phone number and message are required.")
    normalized_number = re.sub(r"[\s().-]", "", phone_number)
    if confirmed is not True:
        raise ValueError("Confirm the WhatsApp message before sending it.")
    if not re.fullmatch(r"\+[1-9]\d{7,14}", normalized_number):
        raise ValueError("Use an international phone number, such as +94771234567.")
    if not message.strip():
        raise ValueError("The WhatsApp message cannot be empty.")

    speak(f"Sending the WhatsApp message to {normalized_number}.")
    threading.Thread(
        target=_send_whatsapp,
        args=(normalized_number, message.strip()),
        daemon=True,
    ).start()
    return "Sending the WhatsApp message. WhatsApp Web must be signed in."


@eel.expose
def createWordDocument(title, content):
    return create_word_document(title, content)


@eel.expose
def draftEmail(recipient, subject, body):
    return draft_email(recipient, subject, body)
