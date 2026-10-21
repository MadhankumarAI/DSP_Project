"""
Experiment 10: Text to Audio
Load pretrained text-to-speech model, provide prompt to convert text
to audio waveform, save generated audio as a .wav file.
"""
import scipy.io.wavfile as wavfile
from transformers import pipeline

# Pretrained text-to-speech model (Bark - takes raw text, returns audio directly)
tts = pipeline("text-to-speech", model="suno/bark-small")

text_prompt = "Hello! This is a demonstration of text to speech generation."
result = tts(text_prompt)

wavfile.write("generated_audio.wav", rate=result["sampling_rate"], data=result["audio"][0])
print("Saved generated_audio.wav")
