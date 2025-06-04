#!/usr/bin/env python3
"""
Oyasumi Discord Bot - Startup Script
Simple script to run the bot from the root directory
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Change to src directory for relative imports
os.chdir(src_path)

# Import and run the bot
from bot import main
import asyncio

if __name__ == "__main__":
    print("Starting Oyasumi Discord Bot...")
    print("Press Ctrl+C to stop the bot")
    print("-" * 40)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"\nBot crashed: {e}")
        sys.exit(1)
