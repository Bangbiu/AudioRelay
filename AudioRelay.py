from AudioIO import *


class AudioRelay():
    def __init__(self):
        self.data_pool: dict = None
        self.streamers: dict = None
        self.proc: dict = None
        self.running = False

        self.clear()

    def clear(self):
        self.data_pool = dict()
        self.streamers = dict()
        self.proc = dict()

        for strm_type in StreamType:
            self.streamers[strm_type] = dict()

        self.running = False

    def build(self, rules):
        self.clear()
        for rule in rules:
            rule_inputs = []
            for ruleID, strm_type, link_type, streamID in rule:
                print("{}, type:{}, link:{}, id:{}".format(ruleID, strm_type, link_type, streamID))
                self.streamers[strm_type][streamID] = AudioRelay.create_streamer(streamID)
                if strm_type == StreamType.Input:
                    rule_inputs.append(streamID)
                else:
                    if streamID in self.proc:
                        self.proc[streamID] += rule_inputs
                    else:
                        self.proc[streamID] = rule_inputs
                    print("Trace: {}, {}".format(streamID, self.proc[streamID]))



    def setpos(self, streamID, pos):
        self.streamers[StreamType.Input][streamID].setpos(pos)

    def start(self):
        print("start")
        for streamID, streamer in self.list_streamer():
            streamer.start()
        self.running = True

    def stop(self):
        for streamID, streamer in self.list_streamer():
            streamer.stop()
        self.running = False

    def list_streamer(self):
        for strm_type in self.streamers.keys():
            streamer: Streamer
            for streamID in self.streamers[strm_type].keys():
                yield streamID, self.streamers[strm_type][streamID]


    def mainloop(self):
        while True:
            if self.running:
                pass

    @staticmethod
    def create_streamer(streamID) -> Streamer:
        if type(streamID) == int:
            info = get_dev_info(streamID)
            if info["streamType"] == StreamDesc[StreamType.Input]:
                return InputCapture(info)
            else:
                return OutputPlayer(info)
        else:
            if os.path.isfile(streamID):
                return WaveCapture(streamID)
            else:
                return WaveRecorder(streamID)