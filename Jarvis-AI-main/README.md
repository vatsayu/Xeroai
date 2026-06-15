# Jarvis AI Assistant

A powerful AI assistant with voice recognition, natural language processing, and various automation capabilities.

## Setup Instructions

1. Install required packages:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
- Copy `.env.example` to `.env`
- Fill in your API keys:
  - WEATHER_API_KEY from [OpenWeatherMap](https://openweathermap.org/api)
  - NEWS_API_KEY from [NewsAPI](https://newsapi.org)
  - OPENAI_API_KEY from [OpenAI](https://openai.com)

## Function Status

### Core Features
- ✅ Speech Recognition
- ✅ Text-to-Speech
- ✅ Natural Language Processing
- ✅ Command Processing

### API-Dependent Features
- ⚠️ Weather Updates (Requires API key)
- ⚠️ News Updates (Requires API key)
- ⚠️ AI Chat (Requires OpenAI API key)

### System Features
- ✅ System Stats
- ✅ File Operations
- ✅ Application Control
- ✅ Web Browsing

### Utility Features
- ✅ Reminders
- ✅ Alarms
- ✅ Notes
- ✅ Calculator
- ✅ Timer

### Media Features
- ✅ Music Playback
- ✅ Screenshots
- ❌ Gesture Recognition (Requires mediapipe setup)

### Smart Home Features
- ⚠️ Device Control (Requires MQTT setup)
- ⚠️ Automation Rules
- ⚠️ Scheduling

### Security Features
- ✅ Encryption
- ✅ Voice Authentication
- ✅ User Management

## Known Issues

1. Gesture recognition is currently disabled (mediapipe commented out)
2. Smart home features require MQTT broker setup
3. Some features require valid API keys to work
4. Voice authentication needs improvement for better security

## Recommendations

1. Use environment variables for sensitive data
2. Set up proper MQTT broker for smart home features
3. Implement proper error handling for API failures
4. Add logging for better debugging
5. Implement rate limiting for API calls
6. Add unit tests for core functions

## Features

### Core Features
- Voice recognition and text-to-speech
- Customizable voice (male/female) and speech rate
- Natural conversation capabilities

### Information & Utilities
- Weather information for any city
- News updates on various categories
- System monitoring (CPU, memory, disk usage)
- Web searching
- Wikipedia facts and random jokes
- Screenshot capture

### Productivity Tools
- Reminders and alarms
- Email sending with attachments
- Calendar information
- Opening websites and applications

### Entertainment
- Music playback via YouTube
- Smart home device control
- Fun facts and jokes

### Personalization
- Customizable user name
- Configurable weather location
- Email credentials management
- Smart home device management

## Installation

1. Clone this repository:
```
git clone https://github.com/yourusername/jarvis-ai.git
cd jarvis-ai
```

2. Install the required dependencies:
```
pip install -r requirements.txt
```

3. Set up API keys:
   - Get a free API key from [OpenWeatherMap](https://openweathermap.org/api) for weather information
   - Get a free API key from [NewsAPI](https://newsapi.org/) for news updates
   - Update the API keys in the `jarvis.py` file

## Usage

Run the assistant:
```
python jarvis.py
```

### Voice Commands

#### Basic Interaction
- "Hello Jarvis" / "Hi Jarvis" - Greet Jarvis
- "How are you" - Check on Jarvis
- "What time is it" - Get current time
- "What's the date" - Get current date
- "Goodbye" / "Bye" - Exit Jarvis

#### Voice Customization
- "Change voice to male" / "Change voice to female" - Switch voice gender
- "Change speed faster" / "Change speed slower" - Adjust speech rate
- "Show voices" / "List voices" - Check available voices

#### Information
- "What's the weather" / "Weather in London" - Get weather information
- "Tell me the news" / "News about technology" - Get news updates
- "System status" - Check system resources
- "Search for Python tutorials" - Web search
- "Tell me a joke" - Get a random joke
- "Tell me a fact" - Get a random fact

#### Productivity
- "Remind me at 3:30 to call John" - Set a reminder
- "Send email" - Send an email (interactive)
- "Take screenshot" - Capture screen

#### Entertainment
- "Play music Despacito" - Play music on YouTube
- "Control light to on" - Control smart home devices

#### Personalization
- "Set my name" - Change how Jarvis addresses you
- "Set weather location" - Change default weather location
- "Set email" - Configure email credentials
- "Add device" - Add a smart home device

#### Applications & Websites
- "Open YouTube" / "Open Google" / "Open Gmail" - Open websites
- "Open Notepad" / "Open Calculator" / "Open Chrome" - Open applications

## Requirements

- Python 3.6+
- Microphone for voice input
- Speakers for voice output
- Internet connection for web features

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Inspired by JARVIS from Iron Man
- Built with Python and various open-source libraries 