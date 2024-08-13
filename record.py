import json
import os
import speech_recognition as sr
import time

def record_text(retries=3):
    # Clear the output.txt file at the start of recording
    with open("output.txt", "w") as f:
        f.write("")

    r = sr.Recognizer()
    for attempt in range(retries):
        try:
            with sr.Microphone() as source2:
                r.adjust_for_ambient_noise(source2, duration=0.5)
                print("Please say something")
                audio2 = r.listen(source2, timeout=5, phrase_time_limit=40)
                MyText = r.recognize_google(audio2)
                return MyText
        except sr.WaitTimeoutError:
            print("Listening timed out while waiting for phrase to start. Retrying...")
        except sr.RequestError as e:
            print(f"Could not request results; {e}. Retrying...")
            time.sleep(1)
        except sr.UnknownValueError:
            print("Unknown error occurred. Retrying...")
            time.sleep(1)
        except ConnectionResetError as e:
            print(f"Connection error: {e}. Retrying...")
            time.sleep(1)
    print("Failed to recognize speech after multiple attempts.")
    return None

def output_text_buffer(text_buffer, file_path="output.txt"):
    with open(file_path, "a") as f:
        for text in text_buffer:
            f.write(text + "\n")

def read_text_file(file_path):
    with open(file_path, "r") as file:
        content = file.read()
    return content
