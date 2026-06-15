#!/usr/bin/env python3
"""
Test script to verify exit commands work properly
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_exit_commands():
    """Test all exit commands to ensure they work"""
    print("Testing Jarvis Exit Commands")
    print("=" * 40)
    
    try:
        from jarvis import respond
        
        # Test various exit commands
        exit_commands = [
            "goodbye",
            "see you later", 
            "bye",
            "farewell",
            "turn off",
            "shutdown",
            "exit",
            "quit",
            "good night",
            "see you tomorrow",
            "adios",
            "later",
            "take care",
            "see ya",
            "peace out",
            "sign off",
            "log off",
            "terminate",
            "finish",
            "shut down",
            "power off",
            "turn off jarvis",
            "close jarvis",
            "end jarvis",
            "stop jarvis",
            "quit jarvis",
            "exit jarvis"
        ]
        
        print("Testing exit commands:")
        print("-" * 30)
        
        for i, cmd in enumerate(exit_commands, 1):
            print(f"{i:2d}. Testing: '{cmd}'")
            
            # Test the command (this will return False for exit commands)
            result = respond(cmd)
            
            if result == False:
                print(f"    [SUCCESS] '{cmd}' correctly triggers exit")
            else:
                print(f"    [FAILED] '{cmd}' did not trigger exit (returned: {result})")
            
            print()
        
        print("Exit command testing completed!")
        print("All exit commands should return False to properly exit the program.")
        
        return True
        
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Test error: {e}")
        return False

if __name__ == "__main__":
    test_exit_commands()
