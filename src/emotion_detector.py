"""
Emotion Detection Module for the Empathy Engine.

This module provides functionality to analyze text and detect emotions using
a combination of traditional NLP techniques and transformer-based models.
"""

from textblob import TextBlob
import nltk
from transformers import pipeline
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure necessary NLTK data is available
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

class EmotionDetector:
    """Class for detecting emotions in text."""
    
    def __init__(self, use_advanced=True):
        """
        Initialize the emotion detector.
        
        Args:
            use_advanced (bool): Whether to use the advanced transformer-based model.
        """
        self.use_advanced = use_advanced
        self.emotion_classifier = None
        
        # Only load the transformer model if advanced detection is requested
        if use_advanced:
            try:
                logger.info("Loading emotion classification model...")
                # Check if internet connection is available
                try:
                    import socket
                    socket.create_connection(("huggingface.co", 443), timeout=3)
                    
                    self.emotion_classifier = pipeline(
                        "text-classification", 
                        model="j-hartmann/emotion-english-distilroberta-base", 
                        return_all_scores=True
                    )
                    logger.info("Emotion classification model loaded successfully")
                except (socket.error, socket.timeout):
                    logger.error("No internet connection available for downloading the model.")
                    logger.warning("Falling back to basic sentiment analysis")
                    self.use_advanced = False
            except Exception as e:
                logger.error(f"Error loading transformer model: {e}")
                logger.warning("Falling back to basic sentiment analysis")
                self.use_advanced = False
    
    def _clean_text(self, text):
        """
        Clean the input text by removing extra spaces, special characters, etc.
        
        Args:
            text (str): The input text to clean.
            
        Returns:
            str: The cleaned text.
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        # Remove URLs
        text = re.sub(r'http\S+', '', text)
        return text
    
    def _basic_sentiment_analysis(self, text):
        """
        Perform basic sentiment analysis using TextBlob.
        
        Args:
            text (str): The text to analyze.
            
        Returns:
            dict: A dictionary with the detected emotion and its confidence score.
        """
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity
        
        # Map polarity to basic emotions
        if polarity > 0.3:
            emotion = "happy"
            score = min(1.0, 0.5 + polarity)
        elif polarity < -0.3:
            emotion = "sad"
            score = min(1.0, 0.5 - polarity)
        elif polarity > 0.1:
            emotion = "positive"
            score = 0.5 + polarity
        elif polarity < -0.1:
            emotion = "negative"
            score = 0.5 - polarity
        else:
            emotion = "neutral"
            score = 1.0 - abs(polarity)
        
        # Adjust score based on subjectivity
        score = score * (0.5 + subjectivity/2)
        
        return {
            "emotion": emotion,
            "score": round(score, 2),
            "details": {
                "polarity": round(polarity, 2),
                "subjectivity": round(subjectivity, 2)
            }
        }
    
    def _advanced_emotion_analysis(self, text):
        """
        Perform advanced emotion analysis using a transformer model.
        
        Args:
            text (str): The text to analyze.
            
        Returns:
            dict: A dictionary with the detected emotions and their confidence scores.
        """
        try:
            results = self.emotion_classifier(text)[0]
            
            # Find the emotion with the highest score
            max_score = 0
            max_emotion = None
            emotions = {}
            
            for result in results:
                emotion = result['label']
                score = result['score']
                emotions[emotion] = round(score, 2)
                
                if score > max_score:
                    max_score = score
                    max_emotion = emotion
            
            return {
                "emotion": max_emotion,
                "score": round(max_score, 2),
                "details": emotions
            }
        except Exception as e:
            logger.error(f"Error in advanced emotion analysis: {e}")
            logger.warning("Falling back to basic sentiment analysis")
            return self._basic_sentiment_analysis(text)
    
    def detect_emotion(self, text):
        """
        Detect the emotion in the provided text.
        
        Args:
            text (str): The text to analyze.
            
        Returns:
            dict: A dictionary with the detected emotion and related information.
        """
        if not text:
            return {"emotion": "neutral", "score": 1.0, "details": {}}
        
        # Clean the text
        cleaned_text = self._clean_text(text)
        
        # Use advanced or basic analysis based on configuration
        if self.use_advanced and self.emotion_classifier:
            result = self._advanced_emotion_analysis(cleaned_text)
        else:
            result = self._basic_sentiment_analysis(cleaned_text)
        
        logger.info(f"Detected emotion: {result['emotion']} (score: {result['score']})")
        return result
    
    def analyze_with_intensity(self, text):
        """
        Analyze text and return emotion with intensity levels.
        
        This method extends the basic emotion detection by adding intensity
        levels that can be used for more granular voice modulation.
        
        Args:
            text (str): The text to analyze.
            
        Returns:
            dict: A dictionary with emotion, intensity, and other details.
        """
        result = self.detect_emotion(text)
        
        # Calculate intensity based on score and other factors
        emotion = result["emotion"]
        score = result["score"]
        
        # Determine intensity level (low, medium, high)
        if score < 0.4:
            intensity = "low"
        elif score < 0.7:
            intensity = "medium"
        else:
            intensity = "high"
        
        # Add exclamation marks, question marks, and all caps as intensity indicators
        exclamations = len(re.findall(r'!', text))
        questions = len(re.findall(r'\?', text))
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text.replace(" ", "")), 1)
        
        # Adjust intensity based on these indicators
        if exclamations > 2 or caps_ratio > 0.3:
            if intensity != "high":
                intensity = "high"
        
        return {
            "emotion": emotion,
            "intensity": intensity,
            "score": score,
            "details": {
                **result.get("details", {}),
                "exclamations": exclamations,
                "questions": questions,
                "caps_ratio": round(caps_ratio, 2)
            }
        }

# Example usage
if __name__ == "__main__":
    detector = EmotionDetector(use_advanced=True)
    
    test_texts = [
        "I'm so excited about this new project!",
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
        print(f"Details: {result['details']}")
