#!/usr/bin/env python3
"""
Simple test for exit commands without full Jarvis initialization
"""

def test_exit_keywords():
    """Test if exit keywords are properly detected"""
    print("Testing Exit Command Keywords")
    print("=" * 40)
    
    # Exit command keywords from jarvis.py
    exit_keywords = [
        'bye', 'goodbye', 'see you later', 'catch you later', 'farewell',
        'turn off', 'shutdown', 'power down', 'exit', 'quit', 'stop',
        'end session', 'close jarvis', 'deactivate', 'disconnect',
        'sleep mode', 'hibernate', 'standby', 'shut down jarvis',
        'turn off jarvis', 'good night', 'see you tomorrow',
        'adios', 'ciao', 'later', 'take care', 'see ya', 'peace out',
        'sign off', 'log off', 'terminate', 'finish', 'done', 'complete',
        'shut down', 'power off', 'turn off jarvis', 'close jarvis',
        'end jarvis', 'stop jarvis', 'quit jarvis', 'exit jarvis'
    ]
    
    # Test queries
    test_queries = [
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
        "done",
        "complete",
        "shut down",
        "power off",
        "turn off jarvis",
        "close jarvis",
        "end jarvis",
        "stop jarvis",
        "quit jarvis",
        "exit jarvis"
    ]
    
    print("Testing exit command detection:")
    print("-" * 30)
    
    for i, query in enumerate(test_queries, 1):
        # Check if any exit word is in the query
        is_exit = any(exit_word in query.lower() for exit_word in exit_keywords)
        
        if is_exit:
            print(f"{i:2d}. [SUCCESS] '{query}' - Exit command detected")
        else:
            print(f"{i:2d}. [FAILED] '{query}' - Exit command NOT detected")
    
    print("\n" + "=" * 40)
    print("Exit command testing completed!")
    print("All commands should be detected as exit commands.")
    print("\nTo test with actual Jarvis, run: python jarvis.py")
    print("Then try saying any of these exit commands.")

if __name__ == "__main__":
    test_exit_keywords()
