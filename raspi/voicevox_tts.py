import requests
import sounddevice as sd
import numpy as np
import json

class VoicevoxTTS:
    def __init__(self, host="localhost", port=50021, speaker=1):
        self.base_url = f"http://{host}:{port}"
        self.speaker = speaker
        sd.default.device = ("hw:2,0", None)

    def synthesize(self, text):
        """テキストから音声データを生成"""
        # 音声合成用クエリを作成
        query = requests.post(
            f"{self.base_url}/audio_query",
            params={"text": text, "speaker": self.speaker}
        )
        if query.status_code != 200:
            raise RuntimeError("audio_query に失敗しました")

        # JSON化して渡す
        query_dict = query.json()

        # 音声合成
        synthesis = requests.post(
            f"{self.base_url}/synthesis",
            headers={"Content-Type": "application/json"},
            params={"speaker": self.speaker},
            data=json.dumps(query_dict, ensure_ascii=False).encode("utf-8")
        )
        if synthesis.status_code != 200:
            raise RuntimeError("synthesis に失敗しました")

        return synthesis.content

    def play(self, wav_data):
        """wavデータを直接再生"""
        import io, wave
        with wave.open(io.BytesIO(wav_data), "rb") as wf:
            samplerate = wf.getframerate()
            channels = wf.getnchannels()
            frames = wf.readframes(wf.getnframes())
            audio = np.frombuffer(frames, dtype=np.int16)
            audio = audio.reshape(-1, channels)
            sd.play(audio, samplerate)
            sd.wait()

    def speak(self, text):
        """テキストを合成して再生"""
        wav_data = self.synthesize(text)
        self.play(wav_data)


if __name__ == "__main__":
    tts = VoicevoxTTS(speaker=1)  # 四国めたん
    tts.speak("こんにちは、ラズベリーパイから音声を再生しています。")


