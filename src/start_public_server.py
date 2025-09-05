"""
Ngrok tunnel setup for the Empathy Engine Flask web application.
This script starts the Flask app and creates a public URL using ngrok.
"""

from pyngrok import ngrok
import os
import subprocess
import time
import sys
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).resolve().parent.parent
if parent_dir not in sys.path:
    sys.path.append(str(parent_dir))

def start_ngrok():
    """Start ngrok tunnel and return the public URL"""
    # Open a ngrok tunnel to the Flask app
    public_url = ngrok.connect(5000)
    print(f" * Ngrok tunnel established at {public_url}")
    print(f" * Share this URL with anyone to let them access your Empathy Engine!")
    print(f" * Press CTRL+C to quit")
    return public_url

if __name__ == "__main__":
    # Start the Flask app in a separate process
    flask_process = subprocess.Popen(
        ["python", os.path.join(parent_dir, "src", "app.py")],
        stdout=subprocess.PIPE
    )
    
    # Wait for Flask to start
    print("Starting Flask application...")
    time.sleep(3)
    
    try:
        # Start ngrok
        public_url = start_ngrok()
        
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        # Clean up on CTRL+C
        print("\nShutting down server...")
        ngrok.kill()
        flask_process.terminate()
