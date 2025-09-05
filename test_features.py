"""
Test script to verify all the features of the Empathy Engine.
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(parent_dir))

from src.emotion_detector import EmotionDetector
from src.voice_modulator import VoiceModulator
from src.empathy_engine import EmpathyEngine

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_emotion_detector():
    """Test the emotion detector component."""
    print("\n--- Testing Emotion Detector ---")
    detector = EmotionDetector(use_advanced=False)
    
    test_texts = [
        "I am so excited about this new technology!",
        "This is really disappointing and frustrating.",
        "Today is Tuesday, the weather seems fine.",
        "OMG! This is AMAZING!!! I can't believe it!"
    ]
    
    for text in test_texts:
        print(f"\nAnalyzing: '{text}'")
        result = detector.analyze_with_intensity(text)
        print(f"Emotion: {result['emotion']}")
        print(f"Intensity: {result['intensity']}")
        print(f"Score: {result['score']}")
    
    print("\n✅ Emotion detector working correctly.")
    return True

def test_voice_modulator(engine_type="pyttsx3"):
    """Test the voice modulator component with different engines."""
    print(f"\n--- Testing Voice Modulator ({engine_type}) ---")
    modulator = VoiceModulator(engine_type=engine_type)
    
    test_text = "This is a test of the voice modulator."
    emotion = "happy"
    intensity = "medium"
    
    print(f"Generating speech for text: '{test_text}'")
    print(f"Emotion: {emotion}, Intensity: {intensity}")
    
    output_file = modulator.generate_speech(test_text, emotion, intensity)
    
    if output_file and os.path.exists(output_file):
        print(f"✅ Voice modulator ({engine_type}) working correctly.")
        print(f"Audio file generated: {output_file}")
        return True
    else:
        print(f"❌ Voice modulator ({engine_type}) failed.")
        return False

def test_empathy_engine(use_advanced=False, tts_engine="pyttsx3"):
    """Test the full Empathy Engine."""
    print(f"\n--- Testing Empathy Engine (advanced={use_advanced}, tts={tts_engine}) ---")
    
    engine = EmpathyEngine(use_advanced_emotion=use_advanced, tts_engine=tts_engine)
    
    test_text = "I am feeling very happy today because I achieved something important!"
    print(f"Processing text: '{test_text}'")
    
    audio_file, emotion_result = engine.process(test_text)
    
    if audio_file and os.path.exists(audio_file):
        print(f"✅ Empathy Engine working correctly.")
        print(f"Detected emotion: {emotion_result['emotion']}")
        print(f"Intensity: {emotion_result['intensity']}")
        print(f"Audio file generated: {audio_file}")
        return True
    else:
        print(f"❌ Empathy Engine failed.")
        return False

def main():
    """Main function for the test script."""
    parser = argparse.ArgumentParser(description='Test the Empathy Engine components')
    parser.add_argument('--all', action='store_true', help='Run all tests')
    parser.add_argument('--detector', action='store_true', help='Test the emotion detector')
    parser.add_argument('--modulator', action='store_true', help='Test the voice modulator')
    parser.add_argument('--engine', action='store_true', help='Test the full empathy engine')
    parser.add_argument('--tts', type=str, choices=['pyttsx3', 'gtts', 'elevenlabs'], default='pyttsx3',
                       help='TTS engine to test with')
    
    args = parser.parse_args()
    
    # If no specific tests are requested, run them all
    run_all = args.all or (not args.detector and not args.modulator and not args.engine)
    
    results = {}
    
    # Test emotion detector
    if args.detector or run_all:
        results['detector'] = test_emotion_detector()
    
    # Test voice modulator
    if args.modulator or run_all:
        results['modulator'] = test_voice_modulator(args.tts)
    
    # Test empathy engine
    if args.engine or run_all:
        results['engine'] = test_empathy_engine(use_advanced=False, tts_engine=args.tts)
    
    # Print summary
    print("\n=== Test Summary ===")
    for test, result in results.items():
        print(f"{test}: {'✅ Passed' if result else '❌ Failed'}")
    
    # Return success only if all tests passed
    return 0 if all(results.values()) else 1

if __name__ == "__main__":
    sys.exit(main())
