#!/usr/bin/env python3
"""
ミニマム構成 Raspberry Pi Whisper STT (クラス版)
"""

import pyaudio
import wave
import whisper

class WhisperSTT:
    def __init__(self, model_name="small", record_seconds=5):
        """
        初期化
        
        Args:
            model_name (str): Whisperモデル名
            record_seconds (int): 録音時間（秒）
        """
        # 設定
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.record_seconds = record_seconds
        self.audio_file = "temp.wav"
        
        # Whisperモデル読み込み
        print(f"Whisperモデル '{model_name}' をロード中...")
        self.model = whisper.load_model(model_name)
        print("モデル読み込み完了")
    
    def record_audio(self):
        """音声録音"""
        audio = pyaudio.PyAudio()
        
        print(f"{self.record_seconds}秒間録音します。話してください...")
        
        # 録音開始
        stream = audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk
        )
        
        frames = []
        for _ in range(int(self.rate / self.chunk * self.record_seconds)):
            data = stream.read(self.chunk)
            frames.append(data)
        
        print("録音完了")
        
        # 録音停止
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        # WAVファイルに保存
        with wave.open(self.audio_file, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(audio.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(frames))
    
    def transcribe(self, language="ja"):
        """
        音声認識
        
        Args:
            language (str): 認識言語
            
        Returns:
            str: 認識結果テキスト
        """
        print("音声認識中...")
        result = self.model.transcribe(self.audio_file, language=language)
        return result["text"]
    
    def run_once(self, language="ja"):
        """
        1回の録音・認識実行
        
        Args:
            language (str): 認識言語
            
        Returns:
            str: 認識結果テキスト
        """
        self.record_audio()
        return self.transcribe(language)
    
    def run_continuous(self, language="ja"):
        """
        連続録音・認識モード
        
        Args:
            language (str): 認識言語
        """
        print("連続モード開始 (Enterで録音、'q'で終了)")
        
        while True:
            user_input = input("\n録音: Enter, 終了: q ").strip().lower()
            
            if user_input == 'q':
                print("終了します")
                break
            
            if user_input == '':
                text = self.run_once(language)
                print(f"認識結果: {text}")

def main():
    
    print("=== Raspberry Pi Whisper STT ===")
    
    # STTインスタンス作成
    stt = WhisperSTT()
    
    # モード選択
    #mode = input("モード選択 (1: 1回のみ, 2: 連続): ").strip()
    
    
    text = stt.run_once()
    print(f"\n認識結果: {text}")

if __name__ == "__main__":
    main()