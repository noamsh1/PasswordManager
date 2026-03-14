import pyaudio
import wave
import threading
import time
import os

MAX_RECORD_SECONDS = 10

class AudioManager:

    def __init__(self, client):
        self.client = client
        self.chunk = 1024  # Record in chunks of 1024 samples
        self.sample_format = pyaudio.paInt16  # 16 bits per sample
        self.channels = 1
        self.fs = 16000  # Record at 16000 samples per second
        self.seconds = MAX_RECORD_SECONDS
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.filename = os.path.join(base_dir, "output.wav")
        self.is_recording = False

    def start_recording(self):
        self.is_recording = True

        self.p = pyaudio.PyAudio()
        self.frames = []  # Initialize array to store frames

        self.stream = self.p.open(format=self.sample_format,
                channels=self.channels,
                rate=self.fs,
                frames_per_buffer=self.chunk,
                input=True)

        threading.Thread(target = self._record_loop, daemon= True).start()

    def _record_loop(self):
        start_time = time.time()
        while self.is_recording and (time.time() - start_time) < self.seconds:
            data = self.stream.read(self.chunk)
            self.frames.append(data)
        
        if self.is_recording:
            self.stop_recording()

    def stop_recording(self):
        self.is_recording = False

        # Stop and close the stream 
        self.stream.stop_stream()
        self.stream.close()

        # Save the recorded data as a WAV file
        wf = wave.open(self.filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.p.get_sample_size(self.sample_format))
        wf.setframerate(self.fs)
        wf.writeframes(b''.join(self.frames))
        wf.close()

        # Terminate the PortAudio interface
        self.p.terminate()

        try:
            self.client.recording_stopped()
        except Exception as e:
            print(e)


    def play_audio(self, filename):
        wf = wave.open(filename, 'rb')

        p = pyaudio.PyAudio()

        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        data = wf.readframes(1024)
        while data:
            stream.write(data)
            data = wf.readframes(1024)

        stream.stop_stream()
        stream.close()
        p.terminate()
