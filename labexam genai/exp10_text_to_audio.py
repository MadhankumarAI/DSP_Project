"""
Experiment 10: Text to Audio
Load pretrained text-to-speech model, provide prompt to convert text
to audio waveform, save generated audio as a .wav file.
"""
import scipy.io.wavfile as wavfile
from transformers import pipeline

prompt="hello everyone this is madhan"

model=pipeline('text-to-speech',model="suno/bark-small")
o=model(prompt)
print(o)
wavfile.write("gen.wav",rate=o['sampling_rate'],data=o['audio'])
print("Saved generated_audio.wav")
