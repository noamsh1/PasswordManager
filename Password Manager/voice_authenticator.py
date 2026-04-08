from vosk import Model, SpkModel, KaldiRecognizer, SetLogLevel
import os
import wave
import json
import numpy as np

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_PATH, "Model")
SPK_MODEL_PATH = os.path.join(BASE_PATH, "SpkModel")
SAMPLES_PER_SECOND = 16000
THRESHOLD = 0.7

class VoiceAuthenticator:
    def __init__(self):
        SetLogLevel(-1) # no vosk logs
        self.model = Model(MODEL_PATH)
        self.spk_model = SpkModel(SPK_MODEL_PATH)

    def calc_voice_signature(self, voice_file):
        rec = KaldiRecognizer(self.model, SAMPLES_PER_SECOND, self.spk_model)
        wf = wave.open(voice_file, "rb")
        data = wf.readframes(4000)
        while data:
            rec.AcceptWaveform(data)
            data = wf.readframes(4000)

        result = json.loads(rec.FinalResult())
        voice_signature = result.get("spk")
        if voice_signature is None:
            return None
        bin_voice_signature = np.array(voice_signature).astype(np.float32).tobytes()
        return bin_voice_signature
    
    def verify_user(self, bin_voice_signature, bin_login_signature):
        v1 = np.frombuffer(bin_voice_signature, dtype = np.float32)
        v2 = np.frombuffer(bin_login_signature, dtype = np.float32)

        similarity = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        print(f"similarity: {similarity}")
        return similarity >= THRESHOLD

