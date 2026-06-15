#!/usr/bin/env python3
"""
Demonstration of Jarvis AI improvements
This script shows how the chatbot now handles repetitive commands intelligently
"""

import sys
import os
import time

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def simulate_conversation():
    """Simulate a conversation to demonstrate the improvements"""
    print("Jarvis AI - Enhanced Chatbot Demo")
    print("=" * 50)
    print("This demo shows how Jarvis now handles repetitive commands intelligently")
    print()
    
    try:
        from jarvis import (
            is_repetitive_command,
            handle_repetitive_command,
            update_conversation_state,
            get_varied_response,
            conversation_state
        )
        
        # Simulate a conversation scenario
        print("[DEMO] Simulating a conversation with repetitive commands:")
        print()
        
        # Scenario 1: User keeps asking for time
        print("Scenario 1: User repeatedly asks for time")
        print("-" * 40)
        
        time_commands = [
            "what time is it",
            "what time is it",  # Repetitive
            "what time is it",  # Still repetitive
            "what's the current time",  # Similar command
        ]
        
        for i, cmd in enumerate(time_commands, 1):
            print(f"User: {cmd}")
            is_repeat, repeat_type = is_repetitive_command(cmd)
            
            if is_repeat:
                response = handle_repetitive_command(cmd, repeat_type)
                print(f"Jarvis: {response}")
            else:
                # Simulate normal response
                response = get_varied_response("time", time="14:30")
                print(f"Jarvis: {response}")
                update_conversation_state(cmd, "time")
            
            print()
            time.sleep(0.5)  # Small delay for realism
        
        # Scenario 2: User asks for weather multiple times
        print("Scenario 2: User asks for weather in different cities")
        print("-" * 40)
        
        weather_commands = [
            "weather in London",
            "weather in Paris",  # Type repeat
            "weather in Tokyo",  # Type repeat
            "what's the temperature in New York",  # Type repeat
        ]
        
        for i, cmd in enumerate(weather_commands, 1):
            print(f"User: {cmd}")
            is_repeat, repeat_type = is_repetitive_command(cmd)
            
            if is_repeat:
                response = handle_repetitive_command(cmd, repeat_type)
                print(f"Jarvis: {response}")
            else:
                # Simulate normal response
                response = get_varied_response("weather", city="London", temp="22", description="sunny")
                print(f"Jarvis: {response}")
                update_conversation_state(cmd, "weather")
            
            print()
            time.sleep(0.5)
        
        # Scenario 3: Mixed commands
        print("Scenario 3: Mixed conversation with some repetition")
        print("-" * 40)
        
        mixed_commands = [
            "hello",
            "what time is it",
            "open notepad",
            "what time is it",  # Repetitive
            "weather in Berlin",
            "open calculator",
            "what time is it",  # Still repetitive
        ]
        
        for i, cmd in enumerate(mixed_commands, 1):
            print(f"User: {cmd}")
            is_repeat, repeat_type = is_repetitive_command(cmd)
            
            if is_repeat:
                response = handle_repetitive_command(cmd, repeat_type)
                print(f"Jarvis: {response}")
            else:
                # Simulate appropriate response
                if "hello" in cmd:
                    response = get_varied_response("greeting")
                elif "time" in cmd:
                    response = get_varied_response("time", time="14:30")
                elif "weather" in cmd:
                    response = get_varied_response("weather", city="Berlin", temp="18", description="rainy")
                else:
                    response = "I understand your request."
                print(f"Jarvis: {response}")
                update_conversation_state(cmd, "mixed")
            
            print()
            time.sleep(0.5)
        
        # Show final conversation state
        print("[INFO] Final Conversation State:")
        print(f"   Current topic: {conversation_state['current_topic']}")
        print(f"   Conversation depth: {conversation_state['conversation_depth']}")
        print()
        
        print("[SUCCESS] Demo completed successfully!")
        print()
        print("Key improvements demonstrated:")
        print("   - Intelligent repetitive command detection")
        print("   - Varied responses to avoid monotony")
        print("   - Context-aware conversation management")
        print("   - Natural conversation flow")
        print()
        print("[READY] Your Jarvis AI is now much smarter!")
        
    except ImportError as e:
        print(f"[ERROR] Import error: {e}")
        print("Make sure jarvis.py is in the same directory")
    except Exception as e:
        print(f"[ERROR] Demo error: {e}")

if __name__ == "__main__":
    simulate_conversation()
