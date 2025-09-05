"""
Main entry point for the Empathy Engine package.
"""

import sys
import os
import logging
from src.cli import main as cli_main
from src.app import app as web_app

def main():
    """
    Main entry point for the Empathy Engine.
    """
    # If no arguments are provided, print help
    if len(sys.argv) == 1:
        print("Empathy Engine - Giving AI a Human Voice")
        print("\nUsage:")
        print("  python -m empathy_engine cli --text 'Your text here' [options]")
        print("  python -m empathy_engine web")
        print("\nFor more information, run:")
        print("  python -m empathy_engine cli --help")
        return 0
    
    # Process the first argument to determine mode
    mode = sys.argv.pop(1).lower()
    
    if mode == "cli":
        return cli_main()
    elif mode == "web":
        web_app.run(debug=True, port=5000)
        return 0
    else:
        print(f"Unknown mode: {mode}")
        print("Available modes: cli, web")
        return 1

if __name__ == "__main__":
    sys.exit(main())
