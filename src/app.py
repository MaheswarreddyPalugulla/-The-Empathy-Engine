"""
Web interface for the Empathy Engine using Flask.
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import sys
import logging
from pathlib import Path
import time

# Add parent directory to path for imports
parent_dir = Path(__file__).resolve().parent.parent
if parent_dir not in sys.path:
    sys.path.append(str(parent_dir))

from src.empathy_engine import EmpathyEngine

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__, 
            template_folder=os.path.join(parent_dir, "templates"),
            static_folder=os.path.join(parent_dir, "static"))

# Create output directory if it doesn't exist
os.makedirs(os.path.join(parent_dir, "output"), exist_ok=True)

# Initialize engine
engine = None

# Create an initialization function
def initialize_engine(use_advanced=False):
    """Initialize the Empathy Engine."""
    global engine
    if engine is None:
        try:
            logger.info(f"Initializing Empathy Engine (use_advanced={use_advanced})")
            engine = EmpathyEngine(use_advanced_emotion=use_advanced)
            logger.info("Empathy Engine initialized for web interface")
        except Exception as e:
            logger.error(f"Error initializing engine: {e}")
            # Create with basic sentiment analysis as fallback
            if use_advanced:
                logger.warning("Falling back to basic sentiment analysis")
                engine = EmpathyEngine(use_advanced_emotion=False)

    # Initialize engine with basic sentiment only
initialize_engine(use_advanced=False)# Use before_request to ensure engine is initialized
@app.before_request
def ensure_engine_initialized():
    if engine is None:
        initialize_engine(use_advanced=False)

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/api/process', methods=['POST'])
def process_text():
    """Process text and generate speech."""
    global engine
    
    # Get request data
    text = request.form.get('text', '')
    voice = request.form.get('voice', 'male')
    tts_engine = request.form.get('engine', 'pyttsx3')
    use_advanced = False  # Always use basic emotion detection
    api_key = request.form.get('api_key', '')
    
    if not text:
        return jsonify({
            'success': False,
            'error': 'No text provided'
        }), 400
        
    # Check if we need API key for ElevenLabs
    if tts_engine == 'elevenlabs' and not api_key:
        return jsonify({
            'success': False,
            'error': 'ElevenLabs API key is required'
        }), 400
    
    try:
        # Check if we should reinitialize the engine
        needs_new_engine = False
        if engine is None:
            needs_new_engine = True
        elif hasattr(engine, 'voice_modulator') and engine.voice_modulator.engine_type != tts_engine:
            needs_new_engine = True
        
        # Initialize or reinitialize engine if needed
        if needs_new_engine:
            try:
                # Set environment variable for API key if provided
                if tts_engine == 'elevenlabs' and api_key:
                    os.environ['ELEVENLABS_API_KEY'] = api_key
                    logger.info("Using provided ElevenLabs API key")
                
                # Try to initialize with requested settings
                engine = EmpathyEngine(use_advanced_emotion=use_advanced, tts_engine=tts_engine)
            except ValueError as ve:
                logger.error(f"Value Error creating engine: {ve}")
                # If it's an API key error, return that to the user
                if "API key" in str(ve):
                    return jsonify({
                        'success': False,
                        'error': str(ve)
                    }), 400
                # Otherwise fall back to basic settings
                engine = EmpathyEngine(use_advanced_emotion=False, tts_engine='pyttsx3')
            except Exception as e:
                logger.error(f"Error creating engine: {e}")
                # Fall back to basic settings
                engine = EmpathyEngine(use_advanced_emotion=False, tts_engine='pyttsx3')
        
        # Set voice
        engine.set_voice(voice)
        
        # Generate unique filename with proper path joining
        timestamp = int(time.time())
        output_file = os.path.join(parent_dir, "output", f"web_{timestamp}.wav")
        
        # Process text
        try:
            audio_file, emotion_result = engine.process(text, output_file)
        except Exception as processing_error:
            logger.error(f"Error in processing: {processing_error}")
            # Try again with basic emotion detection if advanced fails
            if use_advanced:
                logger.info("Retrying with basic emotion detection")
                engine = EmpathyEngine(use_advanced_emotion=False, tts_engine=tts_engine)
                engine.set_voice(voice)
                audio_file, emotion_result = engine.process(text, output_file)
            else:
                raise processing_error
        
        if audio_file and os.path.exists(audio_file):
            # Get relative path for client
            audio_url = f"/audio/{os.path.basename(audio_file)}"
            
            logger.info(f"Generated audio file: {audio_file}")
            logger.info(f"File exists: {os.path.exists(audio_file)}")
            logger.info(f"Sending audio URL to client: {audio_url}")
            
            return jsonify({
                'success': True,
                'audioUrl': audio_url,
                'emotion': emotion_result['emotion'],
                'intensity': emotion_result['intensity'],
                'score': emotion_result['score'],
                'details': emotion_result.get('details', {}),
                'engine': tts_engine,
                'advanced_used': engine.emotion_detector.use_advanced,
                'file_path': audio_file  # Include file path for debugging
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to generate audio file'
            }), 500
            
    except Exception as e:
        logger.error(f"Error processing request: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/audio/<filename>')
def serve_audio(filename):
    """Serve generated audio files."""
    audio_path = os.path.join(parent_dir, "output", filename)
    
    logger.info(f"Requested audio file: {filename}")
    logger.info(f"Looking for audio at path: {audio_path}")
    
    if os.path.exists(audio_path):
        logger.info(f"Found audio file, serving: {audio_path}")
        return send_file(audio_path)
    else:
        logger.error(f"Audio file not found at: {audio_path}")
        # List files in output directory for debugging
        try:
            output_dir = os.path.join(parent_dir, "output")
            if os.path.exists(output_dir):
                files = os.listdir(output_dir)
                logger.info(f"Files in output directory: {files}")
            else:
                logger.error(f"Output directory does not exist: {output_dir}")
        except Exception as e:
            logger.error(f"Error listing output directory: {e}")
            
        return "Audio file not found", 404

if __name__ == "__main__":
    # Ensure output and templates directories exist
    os.makedirs(os.path.join(parent_dir, "output"), exist_ok=True)
    os.makedirs(os.path.join(parent_dir, "templates"), exist_ok=True)
    os.makedirs(os.path.join(parent_dir, "static"), exist_ok=True)
    
    # Run the app
    app.run(debug=True, port=5000)
