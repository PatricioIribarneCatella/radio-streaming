import pyaudio

class AudioPlayer(object):

    def __init__(self, bitrate=16000):

        self.PyAudio = pyaudio.PyAudio
        self.bitrate = bitrate 
        self.p = self.PyAudio()
        self.stream = self.p.open(format = self.p.get_format_from_width(2),
                            channels = 2,
                            rate = bitrate,
                            output = True)

    def play(self, wavedata):
        self.stream.write(wavedata)

    def close(self):
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()