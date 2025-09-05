# The Empathy Engine 🎙️

A service that dynamically modulates the vocal characteristics of synthesized speech based on the detected emotion of the source text. This project bridges the gap between text-based sentiment and expressive, human-like audio output.

## Challenge Objective

The Empathy Engine was built to address the "uncanny valley" problem in AI-driven voice interactions. While AI can understand and generate text with great accuracy, the voice often sounds robotic and lacks emotional nuance. This project enhances TTS systems by adding prosody, emotional range, and subtle vocal cues that build trust and rapport.

## Core Features

1. **Text Input**: Accept text via a web interface or API endpoint
2. **Emotion Detection**: Analyze text to detect emotions and their intensity
3. **Voice Modulation**: Alter vocal parameters (rate, pitch, volume) based on detected emotions
4. **Audio Output**: Generate playable audio files (.mp3, .wav)

## Advanced Features

1. **Granular Emotion Detection**: Detects multiple emotional states:
   - happy, excited, sad, angry, fear, neutral, surprise, positive, negative, concerned
2. **Intensity Scaling**: Modulates voice parameters based on the intensity of the detected emotion (low, medium, high)
3. **Web Interface**: Provides a clean, intuitive interface with text input and an embedded audio player
4. **Multiple TTS Engines**: Supports various TTS engines:
   - pyttsx3 (offline, fast)
   - Google TTS (better quality)
   - ElevenLabs (premium quality, API key required)

## Technical Stack

- **Python**: Core language for all components
- **Emotion Analysis**: TextBlob (basic), HuggingFace Transformers (advanced)
- **TTS Engines**: pyttsx3, Google TTS (gTTS), ElevenLabs API
- **Web Framework**: Flask
- TTS Engines:
  - pyttsx3 (offline) - Default, works without internet
  - gTTS (Google Text-to-Speech API) - Better quality, requires internet
  - ElevenLabs API - Premium quality with SSML support, requires API key
- Web Interface: Flask

## Setup and Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/empathy-engine.git
cd empathy-engine
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download NLTK data (required for TextBlob):
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('vader_lexicon')"
```

5. (Optional) For premium voice quality with ElevenLabs:
   - Create an account at [ElevenLabs](https://beta.elevenlabs.io/)
   - Copy your API key from the account settings
   - Rename `.env.template` to `.env` and add your API key:
```
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM  # You can change this to other voice IDs
```

## Usage

### Command Line Interface

```bash
python src/cli.py --text "I am so excited about this new technology!" --output "output/speech.mp3"
```

### Web Interface

```bash
python src/app.py
```
Then open your browser and navigate to `http://127.0.0.1:5000`

## Design Choices

### Emotion Detection

The system uses a two-tiered approach for emotion detection:
1. Initial sentiment analysis using TextBlob for basic positive/negative classification
2. Advanced emotion classification using a fine-tuned transformer model to detect more nuanced emotions

### Emotion-to-Voice Mapping Logic

The system maps detected emotions to specific voice parameters:

| Emotion    | Rate    | Pitch   | Volume  | Description                          |
|------------|---------|---------|---------|--------------------------------------|
| happy      | +20%    | +15%    | +10%    | Faster, higher pitch, slightly louder|
| excited    | +30%    | +20%    | +15%    | Even faster and higher               |
| sad        | -10%    | -15%    | -10%    | Slower, lower pitch, slightly quieter|
| angry      | +10%    | +5%     | +20%    | Slightly faster, normal pitch, louder|
| fear       | +15%    | +10%    | -5%     | Faster, higher pitch, quieter        |
| neutral    | +0%     | +0%     | +0%     | No modification                      |
| surprise   | +15%    | +20%    | +15%    | Faster, higher pitch, louder         |
| positive   | +10%    | +10%    | +5%     | Slightly faster and higher           |
| negative   | -5%     | -5%     | -5%     | Slightly slower, lower, quieter      |
| concerned  | -5%     | -5%     | +5%     | Slower, lower, slightly louder       |

Additionally, the intensity of the detected emotion (low, medium, high) further scales these modifiers.

## Project Evaluation Criteria

The Empathy Engine meets all core functional requirements and most bonus objectives from the challenge:

### Core Requirements
- ✅ **Text Input**: Accepts text via web interface, CLI, and API
- ✅ **Emotion Detection**: Classifies text into multiple emotional categories
- ✅ **Vocal Parameter Modulation**: Alters rate, pitch, and volume
- ✅ **Emotion-to-Voice Mapping**: Clear logic maps emotions to voice parameters
- ✅ **Audio Output**: Generates playable audio files

### Bonus Objectives
- ✅ **Granular Emotions**: Detects 10 different emotional states
- ✅ **Intensity Scaling**: Adjusts modulation based on emotional intensity
- ✅ **Web Interface**: Provides interactive UI with audio playback
- ❌ **SSML Integration**: Not implemented yet but could be added in future iterations

## Design Choices

The Empathy Engine was built with several key design principles in mind:

1. **Modular Architecture**: The system is split into reusable components (emotion detection, voice modulation) that can be independently improved or replaced.

2. **Tiered Emotion Detection**: 
   - Basic detection uses TextBlob for sentiment analysis - fast and works offline
   - Advanced detection uses transformer models for more nuanced emotion detection

3. **Flexible TTS Engine Support**:
   - Local engine (pyttsx3) for offline use and rapid development
   - Cloud-based engines (gTTS, ElevenLabs) for higher quality when needed

4. **Emotion-to-Voice Parameter Mapping**:
   - Each emotion has specific parameter adjustments based on human speech patterns
   - Intensity scaling ensures proportional voice changes based on emotional intensity
   - Base parameters are modified by percentage rather than absolute values for consistent results

## Project Structure

The repository is organized as follows:

```
empathy_engine/
├── src/                      # Source code
│   ├── app.py                # Flask web interface
│   ├── cli.py                # Command line interface
│   ├── emotion_detector.py   # Emotion detection logic
│   ├── voice_modulator.py    # Voice parameter modulation
│   └── empathy_engine.py     # Main integration module
├── templates/                # HTML templates for web interface
│   └── index.html            # Main web interface
├── output/                   # Directory for generated audio files
├── .env.template             # Template for environment variables
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

## Quick Start Guide

To get started with the Empathy Engine quickly:

1. **Install Dependencies**:
   ```
   pip install -r requirements.txt
   ```

2. **Run the Web Interface**:
   ```
   python src/app.py
   ```
   Then open your browser to http://127.0.0.1:5000/

3. **Use the CLI**:
   ```
   python src/cli.py --text "I am so excited about this new technology!" --output "output/speech.mp3" --voice male --engine pyttsx3
   ```

4. **For Premium Voices (ElevenLabs)**:
   - Copy `.env.template` to `.env`
   - Add your ElevenLabs API key to the `.env` file
   - Select ElevenLabs as the engine in the web interface, or specify `--engine elevenlabs` in the CLI
| Angry | +10% | +5% | +20% |
| Neutral | 0% | 0% | 0% |
| Surprised | +15% | +20% | +15% |
| Concerned | -5% | -5% | +5% |

## License

This project is licensed under the MIT License - see the LICENSE file for details.
