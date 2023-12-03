from AudioIO import *
from os.path import join
import os
import soundfile
from tqdm import tqdm

logRoot = "log"

print("Input Device")
for dev in list_input_device():
    print(dev["desc"])

print("Output Device")
for dev in list_output_device():
    print(dev[ "desc"])

recorder = InputCapture(16, channel=2)
recorder.start()
interval = 5 * recorder.RATE

while True:
    data = recorder.load_chunk()
    for i in tqdm(range(recorder.CHUNK, interval, recorder.CHUNK)):
        chunk = recorder.load_chunk()
        data = np.hstack([data, chunk])
    soundfile.write("seg.wav", data, recorder.RATE)
    break


