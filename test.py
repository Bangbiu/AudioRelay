import audioop
import numpy as np
from AudioIO import *


print("Input Device")
for dev in list_input_device():
    print(dev["desc"])

print("Output Device")
for dev in list_output_device():
    print(dev["desc"])

defout = get_default_output_device()
print(defout)

defin = get_default_input_device()
print(defin)

def downsample(data, channel, in_rate, out_rate):
    new_data, state = audioop.ratecv(data, pyaudio.get_sample_size(pyaudio.paInt16), channel, in_rate,
                                     out_rate, None)
    return new_data

def redirect():
    capture = InputCapture(get_dev_info(19))
    player = OutputPlayer(defout)

    capture.start()
    player.start()

    print(capture.__dict__)
    print(player.__dict__)

    try:
        while True:
            data = capture.load_chunk()
            data = downsample(data, capture.CHANNELS, capture.RATE, player.RATE)
            #print(len(new_data))
            #print(len(data))
            player.write(data)
    except KeyboardInterrupt:
        pass

def player():

    reader = WaveCapture("loopback_record.wav")
    print(reader.get_frame_count())
    #player = WaveRecorder("log/", channels=reader.CHANNELS, rate=reader.RATE)
    player = OutputPlayer(defout)

    player.start()
    reader.start()

    print(player.__dict__)
    print(reader.__dict__)

    data = reader.load_chunk()
    new_data = audioop.ratecv(data, pyaudio.get_sample_size(pyaudio.paInt16), reader.CHANNELS, reader.RATE,
                                     player.RATE, None)[0]
    player.write(new_data)

    sz = len(data)
    print(type(data[0]))

    while len(data) > 0:
        data = reader.load_chunk()
        new_data, state = audioop.ratecv(data, pyaudio.get_sample_size(pyaudio.paInt16), reader.CHANNELS, reader.RATE,
                                         player.RATE, None)
        player.write(new_data)
        sz+=len(data)
        print(sz)

    player.stop()
    reader.stop()

def rediplayer():
    capture = InputCapture(get_dev_info(19))
    reader = WaveCapture("loopback_record.wav")
    player = OutputPlayer(defout)

    capture.start()
    reader.start()
    player.start()

    print(capture.__dict__)
    print(player.__dict__)

    while True:
        cap_data = capture.load_chunk()
        wav_data = reader.load_chunk()
        if len(wav_data) <= 0:
            reader.stream.rewind()

        if capture.RATE != player.RATE:
            cap_data = downsample(cap_data, capture.CHANNELS, capture.RATE, player.RATE)

        if reader.RATE != player.RATE:
            wav_data = downsample(wav_data, reader.CHANNELS, reader.RATE, player.RATE)

        cap_data = np.frombuffer(cap_data, np.int16)
        wav_data = np.frombuffer(wav_data, np.int16)

        if len(wav_data) < len(cap_data):
            padded = np.zeros(len(cap_data), np.int16)
            padded[:len(wav_data)] = wav_data
        else:
            padded = wav_data

        data = cap_data + padded
        #print(len(cap_data))
        #print(len(wav_data))
        print(len(data))

        player.write(data.tobytes())

def rediplayrecord():
    capture = InputCapture(get_dev_info(19))
    reader = WaveCapture("test_audio/loopback_record.wav")
    player = OutputPlayer(defout)
    recorder = WaveRecorder("log/", channels=player.CHANNELS, rate=player.RATE)

    capture.start()
    reader.start()
    player.start()
    recorder.start()

    while True:
        cap_data = capture.load_chunk()
        wav_data = reader.load_chunk()
        if len(wav_data) <= 0:
            reader.stream.rewind()

        if capture.RATE != player.RATE:
            cap_data = downsample(cap_data, capture.CHANNELS, capture.RATE, player.RATE)

        if reader.RATE != player.RATE:
            wav_data = downsample(wav_data, reader.CHANNELS, reader.RATE, player.RATE)

        cap_data = np.frombuffer(cap_data, np.int16)
        wav_data = np.frombuffer(wav_data, np.int16)

        if len(wav_data) < len(cap_data):
            padded = np.zeros(len(cap_data), np.int16)
            padded[:len(wav_data)] = wav_data
        else:
            padded = wav_data

        data = cap_data + padded
        #print(len(cap_data))
        #print(len(wav_data))
        print(len(data))

        player.write(data.tobytes())
        recorder.write(data.tobytes())

#redirect()
#player()
#print(get_dev_info(21))
#rediplayer()
rediplayrecord()