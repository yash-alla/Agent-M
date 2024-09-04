import pyaudio
import speech_recognition as sr
import numpy as np
from queue import Queue
from threading import Thread

# Audio recording parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 1024

# Initialize PyAudio
audio = pyaudio.PyAudio()

# Create a queue to communicate between the audio callback and main thread
q = Queue()

# Initialize recognizer
recognizer = sr.Recognizer()

def audio_callback(in_data, frame_count, time_info, status):
    """This is called (from a separate thread) for each audio block."""
    q.put(in_data)
    return (None, pyaudio.paContinue)

# Find the index of the virtual audio cable input
def find_device_index(device_name):
    for i in range(audio.get_device_count()):
        dev_info = audio.get_device_info_by_index(i)
        if device_name in dev_info['name']:
            return i
    return None

# Get the index of the virtual audio cable input
virtual_cable_index = find_device_index("CABLE Input")

if virtual_cable_index is None:
    raise Exception("Virtual Audio Cable input not found")

# Open the stream
stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    input_device_index=virtual_cable_index,
                    stream_callback=audio_callback)

print("* Recording")
stream.start_stream()

def recognize_worker():
    """Thread to recognize audio chunks."""
    while True:
        try:
            audio_data = b''.join(q.get() for _ in range(int(RATE / CHUNK * 2)))  # Collect ~2 seconds of data
            data = sr.AudioData(audio_data, RATE, 2)
            text = recognizer.recognize_google(data)
            print("Google Speech Recognition thinks you said: " + text)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))

# Start the recognition thread
recognize_thread = Thread(target=recognize_worker)
recognize_thread.daemon = True
recognize_thread.start()

# Record for a specified duration or until interrupted
try:
    while True:
        pass
except KeyboardInterrupt:
    print("* Done recording")
    stream.stop_stream()
    stream.close()
    audio.terminate()
