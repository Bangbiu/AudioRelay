import os

import customtkinter as ctk
from AudioIO import *
from ConfigLoader import config
from tkinter import filedialog
from enum import Enum

ctk.set_appearance_mode("System")  # Modes: system (default), light, dark
ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green


class StreamType(Enum):
    Input = 0
    Output = 1

class LinkType(Enum):
    Device = "Device..."
    File = "File..."


class WinDef(Enum):
    StagePadY = (20, 0)

    RuleHeight = 250
    RulePadY = (0, 20)
    RulePadX = (20, 20)

    StartBtnHeight = 30


StreamDesc = {
    StreamType.Input: "Input",
    StreamType.Output: "Output",
}

StreamIter = {
    StreamType.Input: list_input_device,
    StreamType.Output: list_output_device,
    #StreamType.Loopback: listLoopbackDevices
}

StreamCol = {
    StreamType.Input: 0,
    StreamType.Output: 2
}


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AudioCap")
        self.resizable(False, False)
        self.winSize = [720, 350]
        self.setWinSize()

        self.stage = stage = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        stage.pack(pady=WinDef.StagePadY.value, fill="both", expand=True)
        stage.grid_columnconfigure(0, weight=1)

        self.rules = [RuleFrame(stage, 1)]
        self.placer = RulePlacer(stage)

        self.start_btn = StartButton(stage)

        self.data_pool = dict()
        self.streamers = dict()
        self.streamers[StreamType.Input] = dict()
        self.streamers[StreamType.Output] = dict()

        self.running = False

    def setWinSize(self):
        self.geometry("{}x{}".format(*self.winSize))

    def updateWinSize(self):
        win_h = sum(WinDef.StagePadY.value) + self.start_btn.winfo_height()
        padding = sum(WinDef.RulePadY.value)
        for rule in self.rules:
            win_h += rule.winfo_height() + padding
        self.winSize[1] = win_h + self.placer.winfo_height() + padding
        self.setWinSize()

    def add_rule(self):
        self.placer.set_visible(False)
        self.start_btn.set_visible(False)

        self.rules.append(RuleFrame(self.stage, self.rules.__len__() + 1))
        self.updateWinSize()

        self.placer.set_visible(True)
        self.start_btn.set_visible(True)

    def build_pipeline(self):
        rule: RuleFrame
        for rule in self.rules:
            #print(rule.label.cget("text"))
            for strm_type in StreamType:
                for strm in rule.streams[strm_type]:
                    # print(strm.streamID)
                    if not strm.streamID in self.streamers[strm_type]:
                        self.streamers[strm_type][strm.streamID] = App.create_streamer(strm.streamID)


    def start(self):
        for rule in self.rules:
            rule.procBar.start()

        self.build_pipeline()
        print("start")
        for strm_type in StreamType:
            for streamer in self.streamers[strm_type].values():
                print(type(streamer))
                streamer.start()

        self.summary()

        self.running = True

    def stop(self):
        for rule in self.rules:
            rule.procBar.stop()
        self.running = False

    def summary(self):
        for strm_type in StreamType:
            print(strm_type)
            for streamer in self.streamers[strm_type].values():
                print(type(streamer))

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


class RulePlacer(ctk.CTkFrame):
    def __init__(self, master):
        super(RulePlacer, self).__init__(master=master, height=WinDef.RuleHeight.value)
        self.set_visible(True)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.label = ctk.CTkLabel(self, text="+", fg_color="transparent", font=("Times", 30))
        self.label.pack(fill="both", expand=True)
        self.label.grid(row=0, column=0, padx=20, pady=20)
        self.label.bind("<Button-1>", self.add_rule)

        self.bind("<Button-1>", self.add_rule)

    def add_rule(self, event):
        app.add_rule()

    def set_visible(self, visibility):
        self.visible = visibility
        if self.visible:
            self.pack(pady=WinDef.RulePadY.value, padx=WinDef.RulePadX.value, fill="both", expand=True)
        else:
            self.pack_forget()


class RuleFrame(ctk.CTkFrame):
    def __init__(self, master, index=0):
        super(RuleFrame, self).__init__(master=master, height=WinDef.RuleHeight.value)
        self.pack(pady=(0, 20), padx=20, expand=True)

        self.label = label = ctk.CTkLabel(self, text="Rule {}".format(index))
        label.pack(padx=20, pady=40)
        label.grid(row=1, column=1)

        self.streams = dict()
        self.streams[StreamType.Input] = []
        self.streams[StreamType.Output] = []
        self.procBar = ProcessBar(self)

        self.placers = dict()
        self.placers = [StreamPlacer(self, StreamType.Input), StreamPlacer(self, StreamType.Output)]

    def add_stream(self, type: StreamType, link: LinkType):
        if link == LinkType.Device:
            self.streams[type].append(DeviceMenu(self, type, len(self.streams[type])))
        else:
            if type == StreamType.Input:
                file_path = filedialog.askopenfile(mode='r', filetypes=[("Wave File", "*.wav")]).name
            else:
                file_path = filedialog.askdirectory()
            self.streams[type].append(FileStream(self, type, file_path, len(self.streams[type])))
        # maxLen = max(len(self.inputDevices), len(self.outputDevices))


class StreamPlacer(ctk.CTkOptionMenu):
    def __init__(self, master, type: StreamType):
        super(StreamPlacer, self).__init__(master,
                                           height=40, width=250, corner_radius=20,
                                           fg_color="medium sea green", text_color="black",
                                           button_color="sea green", hover=False,
                                           command=self.add_stream)
        self.type = type
        self.set("Add {} Streamer...".format(StreamDesc[type]))
        self.configure(values=[LinkType.Device.value, LinkType.File.value])
        self.grid(row=0, column=StreamCol[type], padx=20, pady=10)
        self.row = 0

    def add_stream(self, option):
        self.master.add_stream(self.type, LinkType(option))
        self.row += 1
        self.grid(row=self.row, column=StreamCol[self.type], padx=20, pady=10)
        self.set("Add {} Streamer...".format(StreamDesc[self.type]))
        app.updateWinSize()


class FileStream(ctk.CTkFrame):
    def __init__(self, master, type, path, index=0):
        super(FileStream, self).__init__(master, height=40, width=250,
                                         corner_radius=20
                                         )
        self.type = type
        self.path = self.streamID = path
        self.grid(row=index, column=StreamCol[type], padx=20, pady=10)
        self.playing = False
        self.build()

    def build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        if self.type == StreamType.Input:
            self.configure(bg_color="transparent", fg_color="transparent")
            self.ctrl_btn = ctrl_btn = ctk.CTkButton(self, width=20, height=40, corner_radius=20,
                                                     text="▶", command=self.toggle_play,
                                                     fg_color="slate blue", hover_color="dark slate blue")
            ctrl_btn.grid(row=0, column=0)

            self.prog_bar = prog_bar = ctk.CTkSlider(self, width=180, height=20, corner_radius=20,
                                                     progress_color="slate blue", button_hover_color="dark slate blue",
                                                     button_color="slate blue")
            prog_bar.grid(padx=10, row=0, column=1)
            prog_bar.set(0)
        else:
            self.configure(bg_color="transparent", fg_color="slate blue")
            self.out_file_label = label = ctk.CTkLabel(self, text=self.path, text_color="white",
                                                       fg_color="transparent", bg_color="transparent")
            label.grid(row=0, padx=20, pady=10)

    def toggle_play(self):
        self.playing = not self.playing
        self.ctrl_btn.configure(text="||" if self.playing else "▶")


class DeviceMenu(ctk.CTkOptionMenu):
    def __init__(self, master, type, index=0, ignoreIndices=[]):
        super(DeviceMenu, self).__init__(master, height=40, width=250,
                                         values=[], corner_radius=20,
                                         command=self.update_seleted_device)
        self.ignoreIndices = ignoreIndices
        self.type = type
        self.configure(dynamic_resizing=False)
        self.grid(row=index, column=StreamCol[type], padx=20, pady=10)
        self.update_device_list()

        if type == StreamType.Input:
            dev_info = get_default_input_device()
        elif type == StreamType.Output:
            dev_info = get_default_output_device()
        else:
            dev_info = {}

        self.set(dev_info["desc"])
        self.streamID: int = int(dev_info["index"])

    def update_device_list(self):
        names = []
        for info in StreamIter[self.type]():
            if not info["index"] in self.ignoreIndices:
                names.append(info["desc"])
        self.configure(values=names)

    def update_seleted_device(self, option):
        self.streamID = int(option.split(":")[0])


class ProcessBar(ctk.CTkProgressBar):
    def __init__(self, master):
        super(ProcessBar, self).__init__(master, width=100)
        self.grid(row=0, column=1, sticky="ew")
        self.configure(mode="indeterminnate")


class StartButton(ctk.CTkButton):
    def __init__(self, master):
        super(StartButton, self).__init__(master, font=("times", 25), text="▶",
                                          height=WinDef.StartBtnHeight.value,
                                          command=self.toggle_run)
        self.set_visible(True)
        self.running = False

    def toggle_run(self, state="auto"):
        if state == "auto":
            self.running = not self.running
        else:
            self.running = state

        if self.running:
            self.configure(fg_color="red", text="■", hover_color="red4")
            app.start()
        else:
            self.configure(fg_color="#3B8ED0", text="▶", hover_color="#1F6AA5")
            app.stop()

    def set_visible(self, visibility):
        self.visible = visibility
        if self.visible:
            self.pack(pady=WinDef.RulePadY.value, padx=WinDef.RulePadX.value, fill="both", expand=True)
        else:
            self.pack_forget()


if __name__ == "__main__":
    app = App()
    app.mainloop()
"""
while True:
    app.update()
"""
