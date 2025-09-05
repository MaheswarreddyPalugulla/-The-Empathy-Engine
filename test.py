from src.emotion_detector import EmotionDetector
from src.voice_modulator import VoiceModulator
from src.empathy_engine import EmpathyEngine

print("Testing Emotion Detector...")
detector = EmotionDetector(use_advanced=False)
result = detector.analyze_with_intensity('I am so excited about this new technology!')
print(f"Emotion: {result['emotion']}, Intensity: {result['intensity']}")

print("\nTesting Voice Modulator...")
modulator = VoiceModulator(engine_type="pyttsx3")
output_file = modulator.generate_speech("This is a test of the voice modulator.", "neutral", "medium")
print(f"Generated audio file: {output_file}")

print("\nTesting Empathy Engine...")
engine = EmpathyEngine(use_advanced_emotion=False)
audio_file, emotion_result = engine.process("I am feeling very happy today!")
print(f"Detected emotion: {emotion_result['emotion']}, Intensity: {emotion_result['intensity']}")
print(f"Generated audio file: {audio_file}")

print("\nAll tests completed successfully!")
