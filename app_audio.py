import os
import wave
import time
import pyaudio

# region AudioManager
class AudioManager:
    def __init__(self, configManager, controlManager, modelManager, databaseManager, mediaManager):
        self.configManager = configManager
        self.controlManager = controlManager
        self.modelManager = modelManager
        self.databaseManager = databaseManager
        self.mediaManager = mediaManager

        self.audio_loop_time_in_min = self.configManager.get_config("audio_loop_time_in_min") * 60
        self.audio_audio_model = self.configManager.get_config("audio_audio_model")

        self.audio_folder_path = 'data/audios/'
        self.audio_format = pyaudio.paInt16
        self.mia_channels = 2
        self.frame_length = 1024
        self.sample_rate = 44100
        self.default_system_prompt = "You have the audio transcript of my Windows desktop's microphone. It can be a youtube video, rick and morty series, conversation between the user and someone next to them, a zoom call and many others. Describe the transcript and answer with cool details. If you don't know return '-'"

        # Set up recorder
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=self.audio_format,
            channels=self.mia_channels,
            rate=self.sample_rate,
            frames_per_buffer=self.frame_length,
            input=True
        )
    
    def audio_loop(self):
        print(f'Audio Loop...\n')

        if not os.path.exists(self.audio_folder_path):
            os.makedirs(self.audio_folder_path)

        while self.controlManager.is_running():
            rec = []
            current = time.time()
            end = time.time() + self.audio_loop_time_in_min
            
            while current <= end:
                data = self.stream.read(self.frame_length)
                current = time.time()
                rec.append(data)
        
            # Pull data
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            filename = time.strftime('%Y-%m-%d-%H-%M-%S')
            recording_data = b''.join(rec)

            # Save orginal audio to filepath
            audio_filename = f"{filename}.wav"
            audio_path = os.path.join(self.audio_folder_path, audio_filename)
            wf = wave.open(audio_path, 'wb')
            wf.setnchannels(self.mia_channels)
            wf.setsampwidth(self.p.get_sample_size(self.audio_format))
            wf.setframerate(self.sample_rate)
            wf.writeframes(recording_data)
            wf.close()

            # Pass through transcribe API
            transcript_text = self.modelManager.send_audio_to_api(audio_path, self.audio_audio_model)
            # print(f"transcript_text: {transcript_text}")
            
            # Pass transcript through LLM
            payload = {
                "model": "openchat/openchat-3.5-1210",
                "messages": [
                    {
                        "role": "system",
                        "content": self.default_system_prompt
                    },
                    {
                        "role": "user",
                        "content": transcript_text
                    }
                ],
                "max_tokens": 300,
                "temperature": 0.1
            }
            cleaned_transcript_text = self.modelManager.send_text_to_together_api("together", payload)
            # print(f"cleaned_transcript_text: {cleaned_transcript_text}")

            # Save to SQL
            self.databaseManager.save_to_audio_db(timestamp, audio_filename, cleaned_transcript_text)

            if self.controlManager.stop_event.wait(0):
                break