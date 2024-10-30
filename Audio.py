import playsound
import speech_recognition as sr
from gtts import gTTS
from os import remove

r = sr.Recognizer()


def speak(text):
    tts = gTTS(text=text, lang="en")
    filename = "voice.mp3"
    tts.save(filename)
    playsound.playsound("voice.mp3")
    remove("voice.mp3")


def get_audio():
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio)
        except Exception:
            pass

    return said
