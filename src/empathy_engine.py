"""
Main module for the Empathy Engine.

This module integrates emotion detection and voice modulation components.
"""

import os
import logging
from src.emotion_detector import EmotionDetector
from src.voice_modulator import VoiceModulator

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmpathyEngine:
    """Main class for the Empathy Engine that combines emotion detection and voice modulation."""
    
    def __init__(self, use_advanced_emotion=True, tts_engine="pyttsx3"):
        """
        Initialize the Empathy Engine.
        
        Args:
            use_advanced_emotion (bool): Whether to use advanced emotion detection.
            tts_engine (str): The TTS engine to use ('pyttsx3' or 'gtts').
        """
        logger.info(f"Initializing Empathy Engine (advanced_emotion={use_advanced_emotion}, tts_engine={tts_engine})")
        
        self.emotion_detector = EmotionDetector(use_advanced=use_advanced_emotion)
        self.voice_modulator = VoiceModulator(engine_type=tts_engine)
        
    def process(self, text, output_file=None):
        """
        Process text to generate emotionally-appropriate speech.
        
        Args:
            text (str): The input text to process.
            output_file (str, optional): Path to save the output audio file.
            
        Returns:
            tuple: (Path to the generated audio file, Emotion analysis result)
        """
        logger.info(f"Processing text: '{text[:50]}...' (truncated)")
        
        # Detect emotion and intensity
        emotion_result = self.emotion_detector.analyze_with_intensity(text)
        emotion = emotion_result["emotion"]
        intensity = emotion_result["intensity"]
        
        logger.info(f"Detected emotion: {emotion}, intensity: {intensity}")
        
        # Generate speech with appropriate modulation
        audio_file = self.voice_modulator.generate_speech(text, emotion, intensity, output_file)
        
        if audio_file:
            logger.info(f"Generated audio saved to: {audio_file}")
        else:
            logger.error("Failed to generate audio")
        
        return audio_file, emotion_result
        
    def set_voice(self, gender="male"):
        """
        Set the voice type based on gender.
        
        Args:
            gender (str): The gender of the voice to use ('male' or 'female').
            
        Returns:
            bool: True if successful, False otherwise.
        """
        return self.voice_modulator.set_voice(gender)
    
# Example usage
if __name__ == "__main__":
    engine = EmpathyEngine(use_advanced_emotion=True)
    
    test_texts = [
        "I'm so excited about this new project!",
        "This is really disappointing and frustrating.",
        "Today is Tuesday, the weather seems fine.",
        "OMG! This is AMAZING!!! I can't believe it!"
    ]
    
    for text in test_texts:
        print(f"\nProcessing: '{text}'")
        audio_file, emotion_result = engine.process(text)
        print(f"Emotion: {emotion_result['emotion']}")
        print(f"Intensity: {emotion_result['intensity']}")
        print(f"Output file: {audio_file}")
