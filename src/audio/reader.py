import wave

class AudioReader(object):

    def __init__(self, input_file):
        self.wavfile = wave.open(input_file, 'rb')
        self.bitrate = self.wavfile.getframerate()

    def chunks(self):

        window = self.bitrate

        data = self.wavfile.readframes(window)

        while data != "".encode():
            yield data
            data = self.wavfile.readframes(window)

    def reset(self):
        self.wavfile.rewind()


