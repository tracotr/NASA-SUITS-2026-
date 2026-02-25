import sounddevice as sd
from pathlib import Path
from piper import PiperVoice
import threading
import queue
import numpy as np

class TTSEngine:
    def __init__(self, voices_folder="voices", model_name="en_US-hfc_female-medium"):
        '''
        Search for a folder named "voices" in the current directory
        '''
        self.base_dir = Path(__file__).resolve().parent
        self.voice_path = self.base_dir / voices_folder
        
        '''
        Search for voice models with the file type ".onnx" in "voices"
        '''
        self.model_path = self.voice_path / f"{model_name}.onnx"
        self.voice = PiperVoice.load(self.model_path)


        '''
        Set up our worker thread queue, to not block program execution
        '''
        self.queue = queue.Queue()
        self.running = True
        self.thread = threading.Thread(target=self._worker, daemon=True)
        self.thread.start()


    def _worker(self):
        '''
        Background worker that runs in its own thread that waits for text in the queue, and handles
        synthesizing and playing audio.
        '''
        while self.running:
            try:
                # timeout allows for checking if we're still running
                text = self.queue.get(timeout = 0.1)
                if text is None: 
                    break
                
                # synthesize our text, and write to a byte array
                audio_data = b""
                for chunk in self.voice.synthesize(text):
                    if not self.running:
                        break
                    audio_data += chunk.audio_int16_bytes

                # if our byte array as data, store it in an array and send it to sound device to be played
                if audio_data:
                    audio_array = np.frombuffer(audio_data, dtype=np.int16)
                    sd.play(audio_array, samplerate=self.voice.config.sample_rate)
                    sd.wait()
                
                # say we're done with the current task on this thread
                self.queue.task_done() 
            
            # if queue is empty, do nothing
            except queue.Empty:
                continue

    def speak(self, text: str):
        '''
        Puts input text into queue for playback.
        This is non-blocking, so tasks can continue operating after you call this.
        
        :param text: The string of text to be convered to speech.
        :type text: str
        :note: Items are added into a queue, so they are processed in the order they are recieved.
        '''
        self.queue.put(text)

    def clear_queue(self):
        '''
        Clears the queue

        :note: The current audio being spoken will continue, and not be cut off.
        '''
        with self.queue.mutex:
            self.queue.queue.clear()

    def wait(self):
        '''
        Blocks the main program from executing until all items currently queued are finished. 

        :usage: Use after multiple calls to speak() and the audio needs to be synced to a program event
        '''
        self.queue.join()

    def stop(self):
        '''
        Clears the queue and tells sound device to stop playing.
        '''
        self.clear_queue()
        sd.stop()

    def close(self):
        '''
        Shuts down the TTS engine, background thread, and audio stream
        '''
        self.running = False
        self.queue.put(None)
        if self.thread.is_alive():
            self.thread.join()
        self.sd.stop()

    def __enter__(self): 
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        '''
        Upon exiting, wait for our queue to be finished before closing
        ''' 
        self.wait()
        self.close()