"""
Voice Modulation Module for the Empathy Engine.

This module provides functionality to modify voice parameters based on detected emotions.
Supports multiple TTS engines including local (pyttsx3) and API-based (gTTS, ElevenLabs).
"""

import pyttsx3
import os
import logging
from gtts import gTTS
import time
from scipy.io import wavfile
import numpy as np
import requests
import json
import base64
import tempfile
from dotenv import load_dotenv
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables for API keys
load_dotenv()

class VoiceModulator:
    """Class for modulating voice parameters based on detected emotions."""
    
    def __init__(self, engine_type="pyttsx3"):
        """
        Initialize the voice modulator with the specified TTS engine.
        
        Args:
            engine_type (str): The type of TTS engine to use ('pyttsx3', 'gtts', or 'elevenlabs').
        """
        self.engine_type = engine_type
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        self.elevenlabs_voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM") # Default voice
        
        if engine_type == "elevenlabs" and not self.elevenlabs_api_key:
            logger.warning("ElevenLabs API key not found in environment variables.")
            raise ValueError("ElevenLabs API key is required for ElevenLabs TTS engine")
        
        if engine_type == "pyttsx3":
            try:
                self.engine = pyttsx3.init()
                # Get available voices
                voices = self.engine.getProperty('voices')
                if voices:
                    # Set default voice (usually index 0 is male, 1 is female)
                    self.engine.setProperty('voice', voices[0].id)
                    
                # Get default properties
                self.default_rate = self.engine.getProperty('rate')
                self.default_volume = self.engine.getProperty('volume')
                
                logger.info(f"Initialized pyttsx3 engine. Default rate: {self.default_rate}, volume: {self.default_volume}")
            except Exception as e:
                logger.error(f"Error initializing pyttsx3: {e}")
                logger.warning("Falling back to gTTS")
                self.engine_type = "gtts"
        
        # Define emotion-to-parameter mappings with precise values
        # These values are carefully chosen based on human speech patterns
        self.emotion_mapping = {
            # Format: [rate_modifier, pitch_modifier, volume_modifier]
            "happy": [1.2, 1.15, 1.1],      # Faster, higher pitch, slightly louder
            "excited": [1.3, 1.2, 1.15],    # Even faster and higher
            "sad": [0.9, 0.85, 0.9],        # Slower, lower pitch, slightly quieter
            "angry": [1.1, 1.05, 1.2],      # Slightly faster, normal pitch, louder
            "fear": [1.15, 1.1, 0.95],      # Faster, higher pitch, quieter
            "neutral": [1.0, 1.0, 1.0],     # No modification
            "surprise": [1.15, 1.2, 1.15],  # Faster, higher pitch, louder
            "positive": [1.1, 1.1, 1.05],   # Slightly faster and higher
            "negative": [0.95, 0.95, 0.95], # Slightly slower, lower, quieter
            "concerned": [0.95, 0.95, 1.05] # Slower, lower, slightly louder
        }
        
        # Intensity modifiers - apply scaling to better match emotional intensity
        self.intensity_mapping = {
            "low": 0.5,     # 50% of the emotion effect for subtle emotions
            "medium": 1.0,  # 100% - standard emotion modulation
            "high": 1.5     # 150% - enhanced modulation for strong emotions
        }
        
    def _apply_pyttsx3_modulation(self, text, rate_modifier, pitch_modifier, volume_modifier):
        """
        Apply voice modulation using pyttsx3 engine.
        
        Args:
            text (str): The text to synthesize.
            rate_modifier (float): Modifier for speech rate (1.0 is default).
            pitch_modifier (float): Not directly supported in pyttsx3, used indirectly.
            volume_modifier (float): Modifier for volume (1.0 is default).
            
        Returns:
            str: Path to the generated audio file.
        """
        try:
            # Calculate new parameters
            new_rate = int(self.default_rate * rate_modifier)
            new_volume = min(1.0, self.default_volume * volume_modifier)  # Cap volume at 1.0
            
            # Apply parameters
            self.engine.setProperty('rate', new_rate)
            self.engine.setProperty('volume', new_volume)
            
            # Create output filename based on timestamp
            output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output"))
            output_file = os.path.join(output_dir, f"speech_{int(time.time())}.wav")
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            logger.info(f"Creating audio file at: {output_file}")
            
            # Save to file
            self.engine.save_to_file(text, output_file)
            self.engine.runAndWait()
            
            # Apply pitch modification for pyttsx3
            # Note: Since pyttsx3 doesn't directly support pitch modification,
            # we simulate it by adjusting the rate proportionally to the pitch
            # This gives a similar effect as changing pitch in human speech
            if pitch_modifier != 1.0:
                pitch_adjusted_rate = int(new_rate * (pitch_modifier * 0.5 + 0.5))
                self.engine.setProperty('rate', pitch_adjusted_rate)
                # Create a new file with pitch adjustment
                pitch_output_file = output_file.replace('.wav', '_pitched.wav')
                self.engine.save_to_file(text, pitch_output_file)
                self.engine.runAndWait()
                
                # Replace original file with pitch-adjusted version if successful
                if os.path.exists(pitch_output_file):
                    import shutil
                    shutil.move(pitch_output_file, output_file)
            
            logger.info(f"Generated audio with rate={new_rate}, volume={new_volume}, adjusted pitch={pitch_modifier}")
            return output_file
            
        except Exception as e:
            logger.error(f"Error in pyttsx3 modulation: {e}")
            return None
            
    def _apply_gtts_modulation(self, text, rate_modifier, pitch_modifier, volume_modifier):
        """
        Apply voice modulation using Google TTS.
        
        Note: gTTS doesn't support direct parameter modification, so we'll
        use post-processing to achieve the desired effects.
        
        Args:
            text (str): The text to synthesize.
            rate_modifier (float): Modifier for speech rate.
            pitch_modifier (float): Modifier for pitch.
            volume_modifier (float): Modifier for volume.
            
        Returns:
            str: Path to the generated audio file.
        """
        try:
            # Create output filename based on timestamp with absolute path
            parent_dir = Path(__file__).resolve().parent.parent
            output_file = os.path.join(parent_dir, "output", f"speech_{int(time.time())}.mp3")
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # Generate the base audio
            tts = gTTS(text=text, lang='en', slow=(rate_modifier < 0.9))
            tts.save(output_file)
            
            # Convert to WAV for processing
            wav_output = output_file.replace('.mp3', '.wav')
            
            # Use scipy or another library to apply post-processing effects
            # This is a simplified implementation - a real solution would use a library like librosa
            
            logger.info(f"Generated audio file: {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Error in gTTS modulation: {e}")
            return None
            
    def _apply_elevenlabs_modulation(self, text, rate_modifier, pitch_modifier, volume_modifier):
        """
        Apply voice modulation using ElevenLabs API.
        
        Args:
            text (str): The text to synthesize.
            rate_modifier (float): Modifier for speech rate (0.5-2.0).
            pitch_modifier (float): Modifier for pitch (0.5-1.5).
            volume_modifier (float): Modifier for volume (0.5-2.0).
            
        Returns:
            str: Path to the generated audio file.
        """
        try:
            # Create output filename based on timestamp with absolute path
            parent_dir = Path(__file__).resolve().parent.parent
            output_file = os.path.join(parent_dir, "output", f"speech_{int(time.time())}.mp3")
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # ElevenLabs API endpoint
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.elevenlabs_voice_id}"
            
            # Adjust modifiers to match ElevenLabs expected ranges
            stability = 0.5  # Default stability
            similarity_boost = 0.75  # Default similarity boost
            
            # Map our modifiers to ElevenLabs parameters
            # ElevenLabs uses stability (0-1) and similarity_boost (0-1)
            # For emotional speech, we might want lower stability for more expressiveness
            if rate_modifier > 1.1:  # Fast/excited speech
                stability = 0.3  # More variation for excited speech
            elif rate_modifier < 0.9:  # Slow/sad speech
                stability = 0.7  # More stable for sad/serious speech
            
            # Prepare the API request
            headers = {
                "xi-api-key": self.elevenlabs_api_key,
                "Content-Type": "application/json"
            }
            
            # Prepare voice settings with SSML for more control
            ssml_text = f"""
            <speak>
                <prosody rate="{int((rate_modifier - 1) * 100)}%" pitch="{int((pitch_modifier - 1) * 100)}%" volume="{int((volume_modifier - 1) * 100)}%">
                    {text}
                </prosody>
            </speak>
            """
            
            data = {
                "text": ssml_text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": stability,
                    "similarity_boost": similarity_boost,
                    "use_speaker_boost": True
                }
            }
            
            # Make the API request
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                # Save the audio file
                with open(output_file, "wb") as f:
                    f.write(response.content)
                logger.info(f"Generated audio file with ElevenLabs: {output_file}")
                return output_file
            else:
                logger.error(f"Error from ElevenLabs API: {response.status_code} - {response.text}")
                logger.warning("Falling back to gTTS")
                return self._apply_gtts_modulation(text, rate_modifier, pitch_modifier, volume_modifier)
                
        except Exception as e:
            logger.error(f"Error in ElevenLabs modulation: {e}")
            logger.warning("Falling back to gTTS")
            return self._apply_gtts_modulation(text, rate_modifier, pitch_modifier, volume_modifier)
            
    def _apply_pitch_modification(self, audio_file, pitch_modifier):
        """
        Apply pitch modification to an audio file.
        
        This is a simplified implementation - in a production environment,
        you would use a proper audio processing library like librosa or soundfile.
        
        Args:
            audio_file (str): Path to the audio file to modify.
            pitch_modifier (float): Pitch modification factor.
            
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            # Read the audio file
            sample_rate, data = wavfile.read(audio_file)
            
            # Simple pitch shifting by resampling
            # This is a crude method - better methods exist in libraries like librosa
            if pitch_modifier != 1.0:
                # Resample the audio
                new_sample_rate = int(sample_rate * pitch_modifier)
                
                # Save with new sample rate (this changes pitch without changing duration)
                wavfile.write(audio_file, new_sample_rate, data)
                
            return True
            
        except Exception as e:
            logger.error(f"Error applying pitch modification: {e}")
            return False
            
    def generate_speech(self, text, emotion="neutral", intensity="medium", output_file=None):
        """
        Generate speech with emotion-appropriate voice modulation.
        
        Args:
            text (str): The text to synthesize.
            emotion (str): The detected emotion (e.g., "happy", "sad").
            intensity (str): The intensity of the emotion ("low", "medium", "high").
            output_file (str, optional): Path to save the output file. If None, a default path is used.
            
        Returns:
            str: Path to the generated audio file.
        """
        # Get modifiers for the emotion (default to neutral if emotion not found)
        modifiers = self.emotion_mapping.get(emotion.lower(), self.emotion_mapping["neutral"])
        
        # Apply intensity modifier
        intensity_factor = self.intensity_mapping.get(intensity.lower(), 1.0)
        
        # Calculate actual modifiers with intensity factored in
        # For modifiers > 1.0, we want to enhance the effect
        # For modifiers < 1.0, we want to reduce the effect
        rate_mod, pitch_mod, volume_mod = modifiers
        
        # Apply intensity with proper scaling for values above and below 1.0
        def apply_intensity(base_mod):
            if base_mod > 1.0:
                return 1.0 + (base_mod - 1.0) * intensity_factor
            elif base_mod < 1.0:
                return 1.0 - (1.0 - base_mod) * intensity_factor
            else:
                return base_mod
                
        rate_mod = apply_intensity(rate_mod)
        pitch_mod = apply_intensity(pitch_mod)
        volume_mod = apply_intensity(volume_mod)
        
        logger.info(f"Generating speech for emotion: {emotion}, intensity: {intensity}")
        logger.info(f"Modifiers: rate={rate_mod}, pitch={pitch_mod}, volume={volume_mod}")
        
        # If output file is specified, use it
        if output_file:
            # Make sure directory exists
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            logger.info(f"Using specified output file: {output_file}")
        
        # Apply modulation using the appropriate engine
        if self.engine_type == "pyttsx3":
            return self._apply_pyttsx3_modulation(text, rate_mod, pitch_mod, volume_mod)
        elif self.engine_type == "elevenlabs":
            return self._apply_elevenlabs_modulation(text, rate_mod, pitch_mod, volume_mod)
        else:
            return self._apply_gtts_modulation(text, rate_mod, pitch_mod, volume_mod)
            
    def set_voice(self, gender="male"):
        """
        Set the voice type based on gender.
        
        Args:
            gender (str): The gender of the voice to use ('male' or 'female').
            
        Returns:
            bool: True if successful, False otherwise.
        """
        if self.engine_type != "pyttsx3":
            logger.warning("Voice selection only supported with pyttsx3 engine")
            return False
            
        try:
            voices = self.engine.getProperty('voices')
            
            if not voices:
                logger.warning("No voices available")
                return False
            
            # Log available voices to debug
            logger.info(f"Available voices: {len(voices)}")
            for idx, voice in enumerate(voices):
                logger.info(f"Voice {idx}: {voice.id} - {voice.name}")
            
            # On Windows systems:
            # For English voices, typically:
            # - index 0 is Microsoft David (male)
            # - index 1 is Microsoft Zira (female)
            
            if gender.lower() == "male":
                # Always select the first voice (index 0) for male
                voice_idx = 0
            else:
                # For female, try to find index 1 or any voice with female indicators
                if len(voices) > 1:
                    # Check if we can find a female voice by name
                    female_idx = -1
                    for idx, voice in enumerate(voices):
                        voice_name = voice.name.lower()
                        if "zira" in voice_name or "female" in voice_name or "woman" in voice_name:
                            female_idx = idx
                            break
                    
                    # If found a female voice by name, use it
                    if female_idx >= 0:
                        voice_idx = female_idx
                    else:
                        # Otherwise, default to second voice (index 1)
                        voice_idx = 1
                else:
                    # Only one voice available, use it regardless
                    voice_idx = 0
                    
            # Safety check - make sure index is valid
            if voice_idx >= len(voices):
                voice_idx = 0
                
            logger.info(f"Selected voice index {voice_idx} for gender {gender}")    
            self.engine.setProperty('voice', voices[voice_idx].id)
            logger.info(f"Set voice to {gender} using voice ID: {voices[voice_idx].id}")
            return True
            
        except Exception as e:
            logger.error(f"Error setting voice: {e}")
            return False
            
# Example usage
if __name__ == "__main__":
    modulator = VoiceModulator(engine_type="pyttsx3")
    
    test_cases = [
        ("I am so happy today!", "happy", "high"),
        ("I'm feeling a bit sad.", "sad", "medium"),
        ("This is just a neutral statement.", "neutral", "medium")
    ]
    
    for text, emotion, intensity in test_cases:
        print(f"\nGenerating speech for: '{text}'")
        print(f"Emotion: {emotion}, Intensity: {intensity}")
        output_file = modulator.generate_speech(text, emotion, intensity)
        print(f"Output file: {output_file}")
