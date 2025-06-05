"""Text-to-Speech manager"""

import logging
import platform
from typing import Optional
from queue import Queue
import threading

logger = logging.getLogger(__name__)


class TTSManager:
    """Manage Text-to-Speech functionality"""
    
    def __init__(self):
        self.is_enabled = False
        self.voice_queue = Queue()
        self.speaking_thread = None
        self.stop_event = threading.Event()
        self._init_tts_engine()
    
    def _init_tts_engine(self):
        """Initialize TTS engine based on platform"""
        system = platform.system()
        
        try:
            if system == "Darwin":  # macOS
                self.engine_type = "macos"
                import pyttsx3
                self.engine = pyttsx3.init()
                self._configure_voice()
            elif system == "Windows":
                self.engine_type = "windows"
                import pyttsx3
                self.engine = pyttsx3.init('sapi5')
                self._configure_voice()
            else:  # Linux
                self.engine_type = "espeak"
                import pyttsx3
                self.engine = pyttsx3.init('espeak')
                self._configure_voice()
            
            logger.info(f"TTS engine initialized: {self.engine_type}")
            
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
            self.engine = None
    
    def _configure_voice(self):
        """Configure voice settings"""
        if not self.engine:
            return
        
        try:
            # Set voice properties
            self.engine.setProperty('rate', 150)  # Speed
            self.engine.setProperty('volume', 0.9)  # Volume
            
            # Try to set Korean voice if available
            voices = self.engine.getProperty('voices')
            korean_voice = None
            
            for voice in voices:
                if 'korean' in voice.name.lower() or 'ko' in voice.id.lower():
                    korean_voice = voice
                    break
            
            if korean_voice:
                self.engine.setProperty('voice', korean_voice.id)
                logger.info(f"Korean voice set: {korean_voice.name}")
            
        except Exception as e:
            logger.error(f"Failed to configure voice: {e}")
    
    def set_enabled(self, enabled: bool):
        """Enable or disable TTS"""
        self.is_enabled = enabled
        
        if enabled:
            self.start_speaking_thread()
        else:
            self.stop_speaking_thread()
    
    def speak(self, text: str, priority: int = 0):
        """Add text to speech queue"""
        if not self.is_enabled or not self.engine:
            return
        
        # Add to queue with priority (higher priority = speak sooner)
        self.voice_queue.put((-priority, text))
        logger.debug(f"Added to TTS queue: {text[:50]}...")
    
    def speak_now(self, text: str):
        """Speak text immediately (interrupts current speech)"""
        if not self.is_enabled or not self.engine:
            return
        
        try:
            self.engine.stop()  # Stop current speech
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logger.error(f"TTS speak error: {e}")
    
    def start_speaking_thread(self):
        """Start background thread for speech queue"""
        if self.speaking_thread and self.speaking_thread.is_alive():
            return
        
        self.stop_event.clear()
        self.speaking_thread = threading.Thread(target=self._speaking_worker)
        self.speaking_thread.daemon = True
        self.speaking_thread.start()
    
    def stop_speaking_thread(self):
        """Stop speaking thread"""
        self.stop_event.set()
        if self.speaking_thread:
            self.speaking_thread.join(timeout=1)
    
    def _speaking_worker(self):
        """Worker thread for processing speech queue"""
        while not self.stop_event.is_set():
            try:
                # Get from queue with timeout
                priority, text = self.voice_queue.get(timeout=0.5)
                
                if self.engine and self.is_enabled:
                    self.engine.say(text)
                    self.engine.runAndWait()
                
            except:
                # Queue empty or timeout
                continue
    
    def cleanup(self):
        """Cleanup TTS resources"""
        self.stop_speaking_thread()
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass


class MockTTS:
    """Mock TTS for testing without audio"""
    
    def __init__(self):
        self.is_enabled = False
        self.spoken_texts = []
    
    def set_enabled(self, enabled: bool):
        self.is_enabled = enabled
    
    def speak(self, text: str, priority: int = 0):
        if self.is_enabled:
            self.spoken_texts.append(text)
            logger.info(f"[Mock TTS]: {text}")
    
    def speak_now(self, text: str):
        if self.is_enabled:
            self.spoken_texts.append(f"[URGENT] {text}")
            logger.info(f"[Mock TTS - URGENT]: {text}")
    
    def cleanup(self):
        self.spoken_texts.clear()