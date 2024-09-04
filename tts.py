import pyttsx3

# Initialize the engine
engine = pyttsx3.init()

# Get the available voices
voices = engine.getProperty('voices')

# Set the voice to a female voice
# Note: The index for the female voice may vary depending on your system
# Usually, index 1 is for the female voice, but you might need to check
engine.setProperty('voice', voices[1].id)

# Adjust the rate and volume for a more natural sound
engine.setProperty('rate', 175)  # Speed of speech
engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)

def speak(txt):
    engine.say("Hello, I am your female voice assistant. How can I help you today?")
    engine.runAndWait()
