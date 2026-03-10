"""
Quick Start - Launches GUI directly without prompts
"""

import sys
import os

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scripts'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'gui'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'database'))

from main_new import TrafficSystem

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print(" " * 5 + "HU TRAFFIC ANALYZING SYSTEM - Quick Start")
    print("=" * 60 + "\n")
    
    # Launch directly into GUI mode
    system = TrafficSystem()
    system.run_with_gui()
