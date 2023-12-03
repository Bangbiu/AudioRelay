import wave
import os
import pyaudiowpatch as pyaudio
from datetime import datetime
from enum import Enum


class StreamType(Enum):
    Input = 0
    Output = 1


class LinkType(Enum):
    Device = "Device..."
    File = "File..."


StreamDesc = {
    StreamType.Input: "Input",
    StreamType.Output: "Output",
}

ChunkRatio = {
    pyaudio.paInt16: 4
}

def fill_dev_desc(info):
    info["streamType"] = "Input" if info["maxInputChannels"] > 0 else "Output"
    info["desc"] = "{} Device {}: {}".format(info["streamType"], info["index"],
                                             info["name"])
    return info


def get_dev_info(index):
    return fill_dev_desc(p.get_device_info_by_index(index))


def list_audio_device():
    device_count = p.get_device_count()
    for i in range(0, device_count):
        yield get_dev_info(i)


def list_loopback_device():
    return p.get_loopback_device_info_generator()


def list_input_device():
    for info in list_audio_device():
        if info["maxInputChannels"] > 0:
            info["desc"] = info["desc"].replace("Input Device ", "")
            yield info


def list_output_device():
    for info in list_audio_device():
        if info["maxInputChannels"] <= 0:
            info["desc"] = info["desc"].replace("Output Device ", "")
            yield info


def get_default_input_device():
    return get_dev_info(p.get_host_api_info_by_index(0)["defaultInputDevice"])


def get_default_output_device():
    return get_dev_info(p.get_host_api_info_by_index(0)["defaultOutputDevice"])


StreamIter = {
    StreamType.Input: list_input_device,
    StreamType.Output: list_output_device,
    # StreamType.Loopback: listLoopbackDevices
}


class Streamer(object):
    DEF_CHUNK = 2048
    DEF_FORMAT = pyaudio.paInt16

    def __init__(self, dev_info, chunk_size=DEF_CHUNK):
        self.FORMAT = Streamer.DEF_FORMAT
        self.DEVICE = dev_info["index"]
        self.CHUNK = chunk_size

        if dev_info["streamType"] == StreamDesc[StreamType.Input]:
            self.CHANNELS = dev_info["maxInputChannels"]
        else:
            self.CHANNELS = dev_info["maxOutputChannels"]

        self.RATE = int(dev_info["defaultSampleRate"])
        self.stream = None

    def set(self, device, chunk_size, channel, rate=44100):
        self.FORMAT = Streamer.DEF_FORMAT
        self.DEVICE = device
        self.CHUNK = chunk_size
        self.CHANNELS = channel
        self.RATE = rate
        self.stream = None

    def start(self):
        pass

    def stop(self):
        self.stream.close()


class WaveCapture(Streamer):
    def __init__(self, fp, chunk_size=Streamer.DEF_CHUNK):
        wf = wave.open(fp, 'rb')
        super(WaveCapture, self).__init__(WaveCapture.get_wave_file_info(wf), chunk_size)
        self.stream = wf

    def get_frame_count(self):
        return self.stream.getnframes()

    def rewind(self):
        self.stream.rewind()

    def setpos(self, pos):
        self.stream.setpos(pos)

    def load_chunk(self):
        return self.stream.readframes(self.CHUNK)

    @staticmethod
    def get_wave_file_info(wf):
        return {
            "index": -1,
            "streamType": "Input",
            "maxInputChannels": wf.getnchannels(),
            "defaultSampleRate": wf.getframerate()
        }


class InputCapture(Streamer):
    def __init__(self, dev_info, chunk_size=Streamer.DEF_CHUNK):
        super(InputCapture, self).__init__(dev_info, chunk_size)

    def start(self):
        self.stream = p.open(format=self.FORMAT,
                             channels=self.CHANNELS,
                             rate=self.RATE,
                             input=True,
                             output=False,
                             input_device_index=self.DEVICE,
                             # stream_callback=self.callback,
                             frames_per_buffer=self.CHUNK)

    def load_chunk(self):
        return self.stream.read(self.CHUNK)


class WaveRecorder(Streamer):
    def __init__(self, dp, chunk_size=Streamer.DEF_CHUNK, channels=1, rate=44100, file_len=10):
        super(WaveRecorder, self).__init__(WaveRecorder.get_def_wav_info(channels, rate), chunk_size)
        self.dir_path = dp
        self.file_len = file_len
        self.written = 0
        self.stream = None
        self.open()

    def open(self):
        if self.stream is not None:
            self.stop()
        file_path = os.path.join(self.dir_path, "{}.wav".format(datetime.now().strftime('%Y-%m-%d-%H-%M-%S')))
        self.stream = wave.open(file_path, 'wb')
        self.stream.setframerate(self.RATE)
        self.stream.setsampwidth(pyaudio.get_sample_size(Streamer.DEF_FORMAT))
        self.stream.setnchannels(self.CHANNELS)

    def write(self, data):
        self.written += len(data) / ChunkRatio[Streamer.DEF_FORMAT]

        if self.written / self.RATE > self.file_len:
            self.open()
            self.written = 0

        return self.stream.writeframes(data)

    @staticmethod
    def get_def_wav_info(channels=1, rate=44100):
        return {
            "index": -1,
            "streamType": "Output",
            "maxOutputChannels": channels,
            "defaultSampleRate": rate
        }


class OutputPlayer(Streamer):
    def __init__(self, dev_info, chunk_size=Streamer.DEF_CHUNK):
        super(OutputPlayer, self).__init__(dev_info, chunk_size)

    def start(self):
        self.stream = p.open(format=self.FORMAT,
                             channels=self.CHANNELS,
                             rate=self.RATE,
                             input=False,
                             output=True,
                             # stream_callback=self.callback,
                             output_device_index=self.DEVICE,
                             frames_per_buffer=self.CHUNK)

    def write(self, data):
        self.stream.write(data)


p = pyaudio.PyAudio()
