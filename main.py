from threading import Thread, Event
from MainFrame import MainFrame
from AudioRelay import AudioRelay


class Threader(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.start_event = Event()
        self.finish_event = Event()
        self.start()

    def run(self):
        self.start_event.set()
        self.finish_event.set()


class App(Threader):
    def __init__(self):
        super(App, self).__init__()
        self.main_frame: MainFrame = None

    def callback(self):
        self.main_frame.quit()

    def run(self):
        self.main_frame = MainFrame()
        self.start_event.set()
        self.main_frame.protocol("WM_DELETE_WINDOW", self.callback)
        self.main_frame.mainloop()
        self.finish_event.set()


class Backend(Threader):
    def __init__(self):
        super(Backend, self).__init__()
        self.relay: AudioRelay = None

    def run(self):
        self.relay = AudioRelay()
        self.start_event.set()
        self.relay.mainloop()
        self.finish_event.set()


def connect(app: App, backend: Backend):
    app.start_event.wait()
    backend.start_event.wait()

    ui = app.main_frame
    relay = backend.relay
    ui.sender = relay.build
    ui.poseter = relay.setpos
    ui.starter = relay.start
    ui.stoper = relay.stop


if __name__ == "__main__":
    app = App()
    while True:
        pass
    #backend = Backend()
    #connect(app, backend)
