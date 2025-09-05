"""
Command-line interface for the Empathy Engine.
"""

import argparse
import os
import sys
import logging
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).resolve().parent.parent
if parent_dir not in sys.path:
    sys.path.append(str(parent_dir))

from src.empathy_engine import EmpathyEngine

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main function for the CLI."""
    parser = argparse.ArgumentParser(
        description="Empathy Engine - Convert text to emotionally appropriate speech"
    )
    
    # Required arguments
    parser.add_argument(
        "--text", "-t", 
        type=str, 
        help="The text to convert to speech",
        required=True
    )
    
    # Optional arguments
    parser.add_argument(
        "--output", "-o", 
        type=str, 
        help="Path to save the output audio file",
        default=None
    )
    
    parser.add_argument(
        "--engine", "-e", 
        type=str, 
        choices=["pyttsx3", "gtts", "elevenlabs"], 
        help="TTS engine to use",
        default="pyttsx3"
    )
    
    parser.add_argument(
        "--voice", "-v", 
        type=str, 
        choices=["male", "female"], 
        help="Voice type to use",
        default="male"
    )
    
    parser.add_argument(
        "--basic-emotions", "-b", 
        action="store_true", 
        help="Use basic emotion detection instead of advanced"
    )
    
    parser.add_argument(
        "--verbose", 
        action="store_true", 
        help="Enable verbose output"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Set log level based on verbose flag
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create output directory if it doesn't exist
    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    
    try:
        # Initialize the engine
        engine = EmpathyEngine(
            use_advanced_emotion=not args.basic_emotions,
            tts_engine=args.engine
        )
        
        # Set voice
        engine.set_voice(args.voice)
        
        # Process the text
        audio_file, emotion_result = engine.process(args.text, args.output)
        
        if audio_file:
            print(f"\n🎧 Audio generated successfully!")
            print(f"📁 File: {audio_file}")
            print(f"😊 Detected emotion: {emotion_result['emotion']} ({emotion_result['intensity']} intensity)")
            print(f"🔍 Score: {emotion_result['score']}")
            
            if 'details' in emotion_result:
                print("\nEmotion Details:")
                for key, value in emotion_result['details'].items():
                    if isinstance(value, dict):
                        print(f"  {key}:")
                        for subkey, subvalue in value.items():
                            print(f"    {subkey}: {subvalue}")
                    else:
                        print(f"  {key}: {value}")
        else:
            print("\n❌ Failed to generate audio")
            return 1
            
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️ Process interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Error in CLI: {e}", exc_info=args.verbose)
        print(f"\n❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
