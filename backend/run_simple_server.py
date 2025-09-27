#!/usr/bin/env python3
"""
Simple script to run the Volunteer Matching System Simple Server
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from simple_server import main
    print("Starting Volunteer Matching System Simple Server...")
    print("Press Ctrl+C to stop the server")
    main()
except KeyboardInterrupt:
    print("\nServer stopped by user")
except Exception as e:
    print(f"Error starting server: {e}")
    sys.exit(1)
