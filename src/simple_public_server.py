"""
Simple Flask server with ngrok tunnel for the Empathy Engine.
This standalone script creates a minimal version of the app with public access.
"""

from flask import Flask, render_template
from pyngrok import ngrok
import os
import sys
from pathlib import Path

# Get the project root directory
root_dir = Path(__file__).resolve().parent.parent

# Create Flask app
app = Flask(__name__, 
            template_folder=os.path.join(root_dir, "templates"),
            static_folder=os.path.join(root_dir, "static"))

@app.route('/')
def index():
    """Render a simple page demonstrating the ngrok tunnel."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Empathy Engine - Public Demo</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
            h1 { color: #4e73df; }
            .container { max-width: 800px; margin: 0 auto; }
            .info { background: #f5f5f5; padding: 20px; border-radius: 5px; margin-top: 20px; }
            .success { color: green; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎙️ The Empathy Engine</h1>
            <p>This is a public demo of the Empathy Engine, served via ngrok.</p>
            
            <div class="info">
                <p class="success">✅ Ngrok tunnel successfully established!</p>
                <p>This URL can be shared with anyone to access your Empathy Engine.</p>
                <p>For the complete functionality, please run the application locally using:</p>
                <pre>python src/app.py</pre>
            </div>
            
            <h2>About The Empathy Engine</h2>
            <p>The Empathy Engine is a service that dynamically modulates the vocal characteristics of synthesized speech based on the detected emotion of the source text.</p>
            <p>It bridges the gap between text-based sentiment and expressive, human-like audio output by intelligently mapping emotions to voice parameters.</p>
        </div>
    </body>
    </html>
    """

def start_ngrok():
    """Start ngrok tunnel and return the public URL"""
    public_url = ngrok.connect(5000)
    print(f" * Ngrok tunnel established at {public_url}")
    print(f" * Share this URL with anyone to let them access your Empathy Engine!")
    print(f" * Press CTRL+C to quit")
    return public_url

if __name__ == "__main__":
    # Start ngrok
    public_url = start_ngrok()
    
    # Start the Flask app
    app.run()
