import pyttsx3
import speech_recognition as sr
import datetime
import random
import sys
import webbrowser
import os
import subprocess
import time
import requests
import json
import psutil
import platform
import pyautogui
import wikipedia
import smtplib
import pyjokes
import pywhatkit
import threading
import calendar
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import queue
import winsound
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import paho.mqtt.client as mqtt
import yaml
import schedule
import cv2
# import mediapipe as mp
from cryptography.fernet import Fernet
import hashlib
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Global variable to store the current voice settings
current_voice_index = 0
current_rate = 150

# Global variables for reminders
reminders = []
reminder_thread = None

# Global variables for personalization
user_name = "sir"
user_preferences = {
    "weather_location": "India",
    "news_categories": ["technology", "science"],
    "email_address": "",
    "email_password": "",
    "smart_home_devices": []
}

# Global variables for advanced features
conversation_history = []
emotion_state = "neutral"
context_window = 10  # Number of previous interactions to remember
command_history = []  # Track recent commands to avoid repetition
last_command_time = {}  # Track when commands were last executed
conversation_state = {
    "current_topic": None,
    "ongoing_task": None,
    "user_mood": "neutral",
    "conversation_depth": 0
}
learning_data = {
    "preferences": {},
    "routines": {},
    "context": {},
    "personality": {
        "traits": {
            "friendly": 0.8,
            "professional": 0.7,
            "humorous": 0.6,
            "empathetic": 0.9
        },
        "interests": ["technology", "science", "art", "music"],
        "conversation_style": "balanced"  # balanced, formal, casual
    }
}
response_variations = {
    "greeting": [
        "Hello! How can I assist you today?",
        "Hi there! What can I help you with?",
        "Good to see you! How may I be of service?",
        "Hello! I'm here to help. What do you need?"
    ],
    "time": [
        "The current time is {time}",
        "It's {time} right now",
        "The time is {time}",
        "Right now it's {time}"
    ],
    "weather": [
        "The weather in {city} is {temp}°C with {description}",
        "Currently in {city}: {temp}°C, {description}",
        "Weather update for {city}: {temp}°C, {description}",
        "In {city} it's {temp}°C with {description}"
    ],
    "acknowledgment": [
        "I understand",
        "Got it",
        "Understood",
        "I see",
        "Noted"
    ]
}

# API Keys (loaded from environment variables)
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Validate API keys
if not all([WEATHER_API_KEY, NEWS_API_KEY, OPENAI_API_KEY]):
    print("Warning: Some API keys are missing. Please set them in your .env file")
    print("Required environment variables: WEATHER_API_KEY, NEWS_API_KEY, OPENAI_API_KEY")

print("\nAPI keys have been set. Starting Jarvis...")

# Smart Home Configuration
SMART_HOME_CONFIG = {
    "mqtt_broker": "localhost",
    "mqtt_port": 1883,
    "devices": {}
}

# Security Configuration
SECURITY_CONFIG = {
    "voice_auth_enabled": False,
    "encryption_key": None,
    "authorized_users": {}
}

# Initialize speech recognizer with error handling
def initialize_recognizer():
    """Initialize the speech recognizer with error handling"""
    try:
        r = sr.Recognizer()
        # Test microphone access
        with sr.Microphone() as source:
            print("Testing microphone access...")
            r.adjust_for_ambient_noise(source, duration=1)
            print("Microphone access successful!")
        return r
    except Exception as e:
        print(f"Error initializing microphone: {str(e)}")
        print("Please check if your microphone is properly connected and has necessary permissions.")
        return None

# Initialize text-to-speech engine with error handling
def initialize_tts():
    """Initialize the text-to-speech engine with error handling"""
    try:
        engine = pyttsx3.init()
        
        # Get available voices
        voices = engine.getProperty('voices')
        
        # Set default voice to male (index 0)
        if len(voices) > 0:
            engine.setProperty('voice', voices[0].id)  # Male voice
            engine.setProperty('rate', 180)  # Default speed
        
        return engine
    except Exception as e:
        print(f"Error initializing TTS engine: {str(e)}")
        print("Please make sure you have the required text-to-speech voices installed.")
        return None

# Initialize the recognizer and TTS engine
r = initialize_recognizer()
engine = initialize_tts()

if r is None:
    print("Failed to initialize microphone. Please check your microphone settings and try again.")
    exit(1)

if engine is None:
    print("Failed to initialize text-to-speech. Some features may be limited.")
    # Continue with limited functionality
    engine = None

def speak(text):
    """Convert text to speech with error handling"""
    try:
        if engine is not None:
            # Get current voice settings
            voices = engine.getProperty('voices')
            if voices and len(voices) > current_voice_index:
                engine.setProperty('voice', voices[current_voice_index].id)
            engine.setProperty('rate', current_rate)
            engine.say(text)
            engine.runAndWait()
        else:
            print(text)  # Fallback to printing text if speech fails
    except Exception as e:
        print(f"Error in text-to-speech: {str(e)}")
        print(text)  # Fallback to printing text if speech fails

def change_voice(gender="female", rate=None):
    """Change the voice gender and rate"""
    global engine, current_voice_index, current_rate
    
    try:
        voices = engine.getProperty('voices')
        
        if gender.lower() == "female":
            if len(voices) > 1:
                engine.setProperty('voice', voices[1].id)
                current_voice_index = 1
                speak("Voice changed to female")
            else:
                speak("Female voice not available")
        elif gender.lower() == "male":
            if len(voices) > 0:
                engine.setProperty('voice', voices[0].id)
                current_voice_index = 0
                speak("Voice changed to male")
            else:
                speak("Male voice not available")
        
        if rate is not None:
            engine.setProperty('rate', rate)
            current_rate = rate
            speak(f"Speech rate set to {rate}")
            
    except Exception as e:
        speak(f"Error changing voice: {str(e)}")

def list_voices():
    """List all available voices"""
    try:
        voices = engine.getProperty('voices')
        speak(f"I found {len(voices)} voices:")
        
        for i, voice in enumerate(voices):
            gender = "Female" if "female" in voice.name.lower() else "Male"
            speak(f"Voice {i+1}: {gender} voice")
            
    except Exception as e:
        speak(f"Error listing voices: {str(e)}")

def wishMe():
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        speak("Good Morning!")
    elif 12 <= hour < 18:
        speak("Good Afternoon!")
    else:
        speak("Good Evening!")
    speak("I am Jarvis AI, How can I help you sir?")

def listen():
    """Enhanced listening with better error handling and multiple recognition attempts"""
    try:
        with sr.Microphone() as source:
            print("Listening...")
            r.pause_threshold = 0.8  # Reduced for faster response
            r.energy_threshold = 300  # Adjust for ambient noise
            r.dynamic_energy_threshold = True
            
            # Try multiple recognition attempts
            for attempt in range(3):
                try:
                    audio = r.listen(source, timeout=8, phrase_time_limit=10)
                    print("Recognizing...")
                    
                    # Try multiple recognition services
                    try:
                        query = r.recognize_google(audio, language='en-US')
                    except:
                        try:
                            query = r.recognize_google(audio, language='en-IN')
                        except:
                            query = r.recognize_google(audio)
                    
                    print(f"User said: {query}")
                    return query.lower()
                    
                except sr.UnknownValueError:
                    if attempt < 2:
                        print("I didn't catch that clearly. Please try again...")
                        speak("I didn't catch that clearly. Please try again.")
                        continue
                    else:
                        print("Sorry, I couldn't understand. Please speak more clearly.")
                        speak("Sorry, I couldn't understand. Please speak more clearly.")
                        return ""
                        
                except sr.RequestError as e:
                    print(f"Recognition service error: {e}")
                    if attempt < 2:
                        speak("Having trouble with recognition. Let me try again.")
                        continue
                    else:
                        speak("I'm having trouble with voice recognition. Please try again.")
                        return ""
                        
                except Exception as e:
                    print(f"Recognition error: {str(e)}")
                    if attempt < 2:
                        continue
                    else:
                        speak("I encountered an error. Please try again.")
                        return ""
            
            return ""
            
    except Exception as e:
        print(f"Error accessing microphone: {str(e)}")
        speak("I'm having trouble accessing the microphone. Please check your microphone settings.")
        return ""

def listen_continuous():
    """Continuous listening mode for wake word detection"""
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=1)
            print("Continuous listening mode activated. Say 'Hey Jarvis' to wake me up.")
            
            while True:
                try:
                    audio = r.listen(source, timeout=1, phrase_time_limit=3)
                    query = r.recognize_google(audio, language='en-US').lower()
                    
                    # Check for wake words
                    wake_words = ['hey jarvis', 'jarvis', 'assistant', 'wake up', 'listen']
                    if any(wake_word in query for wake_word in wake_words):
                        print("Wake word detected!")
                        speak("Yes, I'm listening. How can I help you?")
                        return listen()  # Switch to normal listening
                        
                except sr.UnknownValueError:
                    continue  # Keep listening
                except sr.RequestError:
                    time.sleep(0.1)
                    continue
                except Exception:
                    continue
                    
    except Exception as e:
        print(f"Continuous listening error: {str(e)}")
        return ""

def open_website(url, site_name):
    # First speak the site name
    speak(f"Opening {site_name}")
    # Then open the website after a short delay
    time.sleep(0.5)
    webbrowser.open(url)

def open_application(app_name):
    try:
        if app_name == "notepad":
            subprocess.Popen("notepad.exe")
            speak("Opening Notepad")
        elif app_name == "calculator":
            subprocess.Popen("calc.exe")
            speak("Opening Calculator")
        elif app_name == "paint":
            subprocess.Popen("mspaint.exe")
            speak("Opening Paint")
        elif app_name == "word":
            # Try different possible paths for Microsoft Word
            word_paths = [
                "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE",
                "C:\\Program Files\\Microsoft Office\\Office16\\WINWORD.EXE",
                "C:\\Program Files (x86)\\Microsoft Office\\Office16\\WINWORD.EXE",
                "C:\\Program Files\\Microsoft Office\\root\\Office15\\WINWORD.EXE",
                "C:\\Program Files\\Microsoft Office\\Office15\\WINWORD.EXE",
                "C:\\Program Files (x86)\\Microsoft Office\\Office15\\WINWORD.EXE",
                "C:\\Program Files\\Microsoft Office\\root\\Office14\\WINWORD.EXE",
                "C:\\Program Files\\Microsoft Office\\Office14\\WINWORD.EXE",
                "C:\\Program Files (x86)\\Microsoft Office\\Office14\\WINWORD.EXE",
                "winword.exe"  # Fallback to PATH search
            ]
            for path in word_paths:
                if os.path.exists(path):
                    subprocess.Popen(path)
                    speak("Opening Microsoft Word")
                    break
            else:
                speak("Could not find Microsoft Word. Please make sure it's installed.")
        elif app_name == "excel":
            # Try different possible paths for Microsoft Excel
            excel_paths = [
                "C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE",
                "C:\\Program Files\\Microsoft Office\\Office16\\EXCEL.EXE",
                "C:\\Program Files (x86)\\Microsoft Office\\Office16\\EXCEL.EXE",
                "C:\\Program Files\\Microsoft Office\\root\\Office15\\EXCEL.EXE",
                "C:\\Program Files\\Microsoft Office\\Office15\\EXCEL.EXE",
                "C:\\Program Files (x86)\\Microsoft Office\\Office15\\EXCEL.EXE",
                "C:\\Program Files\\Microsoft Office\\root\\Office14\\EXCEL.EXE",
                "C:\\Program Files\\Microsoft Office\\Office14\\EXCEL.EXE",
                "C:\\Program Files (x86)\\Microsoft Office\\Office14\\EXCEL.EXE",
                "excel.exe"  # Fallback to PATH search
            ]
            for path in excel_paths:
                if os.path.exists(path):
                    subprocess.Popen(path)
                    speak("Opening Microsoft Excel")
                    break
            else:
                speak("Could not find Microsoft Excel. Please make sure it's installed.")
        elif app_name == "powerpoint":
            # Try different possible paths for Microsoft PowerPoint
            ppt_paths = [
                "C:\\Program Files\\Microsoft Office\\root\\Office16\\POWERPNT.EXE",
                "C:\\Program Files\\Microsoft Office\\Office16\\POWERPNT.EXE",
                "C:\\Program Files (x86)\\Microsoft Office\\Office16\\POWERPNT.EXE",
                "C:\\Program Files\\Microsoft Office\\root\\Office15\\POWERPNT.EXE",
                "C:\\Program Files\\Microsoft Office\\Office15\\POWERPNT.EXE",
                "C:\\Program Files (x86)\\Microsoft Office\\Office15\\POWERPNT.EXE",
                "C:\\Program Files\\Microsoft Office\\root\\Office14\\POWERPNT.EXE",
                "C:\\Program Files\\Microsoft Office\\Office14\\POWERPNT.EXE",
                "C:\\Program Files (x86)\\Microsoft Office\\Office14\\POWERPNT.EXE",
                "powerpnt.exe"  # Fallback to PATH search
            ]
            for path in ppt_paths:
                if os.path.exists(path):
                    subprocess.Popen(path)
                    speak("Opening Microsoft PowerPoint")
                    break
            else:
                speak("Could not find Microsoft PowerPoint. Please make sure it's installed.")
        elif app_name == "chrome":
            # Try different possible paths for Google Chrome
            chrome_paths = [
                "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
                "C:\\Users\\%USERNAME%\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe",
                "chrome.exe"  # Fallback to PATH search
            ]
            for path in chrome_paths:
                expanded_path = os.path.expandvars(path)
                if os.path.exists(expanded_path):
                    subprocess.Popen(expanded_path)
                    speak("Opening Google Chrome")
                    break
            else:
                # If Chrome not found, try to open it through the default browser
                webbrowser.get('chrome').open('https://www.google.com')
                speak("Opening Google Chrome")
        elif app_name == "explorer":
            subprocess.Popen("explorer.exe")
            speak("Opening File Explorer")
        else:
            speak(f"Sorry, I don't know how to open {app_name}")
    except Exception as e:
        speak(f"Sorry, I couldn't open {app_name}. {str(e)}")

def get_weather(city=None):
    """Get weather information for a city"""
    if city is None:
        city = user_preferences["weather_location"]
    
    try:
        # Use the correct OpenWeatherMap API endpoint
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            temp = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            description = data["weather"][0]["description"]
            feels_like = data["main"]["feels_like"]
            
            # Use varied response for weather
            weather_info = get_varied_response("weather", 
                                             city=city, 
                                             temp=temp, 
                                             description=description)
            speak(weather_info)
            return weather_info
        else:
            error_message = data.get("message", "Unknown error")
            speak(f"Sorry, I couldn't get weather information for {city}. Error: {error_message}")
            return None
    except requests.exceptions.RequestException as e:
        speak(f"Error connecting to weather service. Please check your internet connection.")
        print(f"Network error: {str(e)}")
        return None
    except Exception as e:
        speak(f"Error getting weather information: {str(e)}")
        print(f"Error: {str(e)}")
        return None

def get_news(category=None):
    """Get news headlines for a category"""
    if category is None:
        category = random.choice(user_preferences["news_categories"])
    
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=us&category={category}&apiKey={NEWS_API_KEY}"
        response = requests.get(url)
        data = json.loads(response.text)
        
        if response.status_code == 200 and data["status"] == "ok":
            articles = data["articles"][:5]  # Get top 5 articles
            
            speak(f"Here are the top {category} news headlines:")
            for i, article in enumerate(articles, 1):
                title = article["title"]
                speak(f"{i}. {title}")
            
            return articles
        else:
            speak(f"Sorry, I couldn't get news for {category}")
            return None
    except Exception as e:
        speak(f"Error getting news: {str(e)}")
        return None

def system_stats():
    """Get system statistics"""
    try:
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        stats = f"CPU usage is {cpu_percent}%. Memory usage is {memory.percent}%. Disk usage is {disk.percent}%."
        speak(stats)
        return stats
    except Exception as e:
        speak(f"Error getting system stats: {str(e)}")
        return None

def set_reminder(time_str, message):
    """Set a reminder for a specific time"""
    try:
        # Parse time string (format: HH:MM)
        hour, minute = map(int, time_str.split(':'))
        
        # Create reminder object
        reminder = {
            "time": time_str,
            "message": message,
            "triggered": False
        }
        
        reminders.append(reminder)
        speak(f"Reminder set for {time_str}: {message}")
        
        # Start reminder thread if not already running
        global reminder_thread
        if reminder_thread is None or not reminder_thread.is_alive():
            reminder_thread = threading.Thread(target=check_reminders)
            reminder_thread.daemon = True
            reminder_thread.start()
        
        return reminder
    except Exception as e:
        speak(f"Error setting reminder: {str(e)}")
        return None

def check_reminders():
    """Check for reminders that need to be triggered"""
    while True:
        current_time = datetime.datetime.now().strftime("%H:%M")
        
        for reminder in reminders:
            if reminder["time"] == current_time and not reminder["triggered"]:
                speak(f"Reminder: {reminder['message']}")
                reminder["triggered"] = True
        
        # Sleep for 30 seconds before checking again
        time.sleep(30)

def web_search(query):
    """Perform a web search"""
    try:
        speak(f"Searching for {query}")
        # Use pywhatkit with a longer wait time and auto-close
        pywhatkit.search(query, wait=15, close=3)
        return True
    except Exception as e:
        speak(f"Error performing web search: {str(e)}")
        return False

def send_email(to_email, subject, body, attachment_path=None):
    """Send an email"""
    try:
        if not user_preferences["email_address"] or not user_preferences["email_password"]:
            speak("Email credentials not set. Please set your email and password first.")
            return False
        
        msg = MIMEMultipart()
        msg['From'] = user_preferences["email_address"]
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, 'rb') as file:
                attachment = MIMEApplication(file.read(), _subtype="txt")
                attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment_path))
                msg.attach(attachment)
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(user_preferences["email_address"], user_preferences["email_password"])
        server.send_message(msg)
        server.quit()
        
        speak(f"Email sent to {to_email}")
        return True
    except Exception as e:
        speak(f"Error sending email: {str(e)}")
        return False

def play_music(song_name=None):
    """Play music on YouTube"""
    try:
        if song_name:
            # Clean and format the song name for better search results
            song_name = song_name.strip()
            # Add 'official video' to improve search accuracy
            search_query = f"{song_name} official video"
            speak(f"Playing {song_name} on YouTube")

            try:
                # Use pywhatkit without wait and close parameters
                pywhatkit.playonyt(search_query)
            except Exception as e:
                print(f"Direct YouTube search failed: {str(e)}")
                # Fallback to web search with encoded query
                encoded_query = search_query.replace(" ", "+")
                webbrowser.open(f"https://www.youtube.com/results?search_query={encoded_query}")
        else:
            speak("What song would you like me to play?")
            song_query = listen()
            if song_query != "":
                play_music(song_query)
    except Exception as e:
        speak(f"Error playing music: {str(e)}")
        return False
    return True

def control_smart_home(device, action):
    """Control smart home devices"""
    try:
        if device not in user_preferences["smart_home_devices"]:
            speak(f"Device {device} not found in your smart home setup")
            return False
        
        # This is a placeholder for actual smart home integration
        # You would need to implement the actual API calls to your smart home system
        speak(f"Controlling {device} to {action}")
        return True
    except Exception as e:
        speak(f"Error controlling smart home: {str(e)}")
        return False

def tell_joke():
    """Tell a random joke"""
    try:
        joke = pyjokes.get_joke()
        speak(joke)
        return joke
    except Exception as e:
        speak(f"Error telling joke: {str(e)}")
        return None

def tell_fact():
    """Tell a random fact"""
    try:
        # Get a random Wikipedia article
        random_page = wikipedia.random(1)
        summary = wikipedia.summary(random_page, sentences=1)
        speak(summary)
        return summary
    except Exception as e:
        speak(f"Error telling fact: {str(e)}")
        return None

def set_user_preference(preference, value):
    """Set a user preference"""
    try:
        if preference in user_preferences:
            user_preferences[preference] = value
            speak(f"Preference {preference} set to {value}")
            return True
        else:
            speak(f"Preference {preference} not found")
            return False
    except Exception as e:
        speak(f"Error setting preference: {str(e)}")
        return False

def set_email_credentials(email, password):
    """Set email credentials for sending emails"""
    try:
        user_preferences["email_address"] = email
        user_preferences["email_password"] = password
        speak("Email credentials set successfully")
        return True
    except Exception as e:
        speak(f"Error setting email credentials: {str(e)}")
        return False

def add_smart_home_device(device):
    """Add a smart home device to the list"""
    try:
        if device not in user_preferences["smart_home_devices"]:
            user_preferences["smart_home_devices"].append(device)
            speak(f"Device {device} added to your smart home setup")
            return True
        else:
            speak(f"Device {device} already exists in your smart home setup")
            return False
    except Exception as e:
        speak(f"Error adding smart home device: {str(e)}")
        return False

def take_screenshot():
    """Take a screenshot"""
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        speak(f"Screenshot saved as {filename}")
        return filename
    except Exception as e:
        speak(f"Error taking screenshot: {str(e)}")
        return None

def calculate(expression):
    """Perform basic calculations with improved error handling"""
    try:
        # Replace words with operators
        expression = expression.lower()
        expression = expression.replace('plus', '+')
        expression = expression.replace('minus', '-')
        expression = expression.replace('multiply by', '*')
        expression = expression.replace('times', '*')
        expression = expression.replace('divided by', '/')
        expression = expression.replace('divide by', '/')
        
        # Remove any non-math characters
        expression = ''.join(c for c in expression if c.isdigit() or c in '+-*/() .')
        
        # Handle multiplication and division
        expression = expression.replace('x', '*')
        expression = expression.replace('×', '*')
        expression = expression.replace('÷', '/')
        
        # Evaluate the expression
        result = eval(expression)
        
        # Format the result
        if isinstance(result, float):
            if result.is_integer():
                result = int(result)
            else:
                result = round(result, 2)
        
        speak(f"The result is {result}")
        return result
    except ZeroDivisionError:
        speak("I cannot divide by zero")
        return None
    except Exception as e:
        speak("I couldn't calculate that. Please try again with a valid expression.")
        print(f"Calculation error: {str(e)}")
        return None

def ai_search(query):
    """Perform an AI-powered search using OpenAI API with improved response handling"""
    try:
        speak(f"Searching for information about {query}")
        
        # Prepare the API request
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "You are a helpful AI assistant. Provide clear, concise, and accurate information in a conversational way. Break down complex topics into simple explanations."},
                {"role": "user", "content": f"Please explain: {query}"}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        # Make the API request with timeout
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result['choices'][0]['message']['content']
            
            # Process and speak the answer in chunks
            speak("Here's what I found:")
            
            # Split the answer into sentences for better speech
            sentences = answer.split('. ')
            current_chunk = ""
            
            for sentence in sentences:
                if sentence.strip():  # Skip empty sentences
                    if len(current_chunk) + len(sentence) < 150:
                        current_chunk += sentence + ". "
                    else:
                        speak(current_chunk.strip())
                        current_chunk = sentence + ". "
                        time.sleep(0.5)  # Add a small pause between chunks
            
            # Speak any remaining text
            if current_chunk.strip():
                speak(current_chunk.strip())
            
            return answer
        else:
            error_msg = f"Error from OpenAI API: {response.status_code} - {response.text}"
            speak("I'm having trouble getting information from the AI. Let me try a different approach.")
            print(error_msg)
            return None
            
    except requests.exceptions.Timeout:
        speak("The AI search is taking longer than expected. Let me try again.")
        return None
    except requests.exceptions.RequestException as e:
        speak("I'm having trouble connecting to the AI service. Please check your internet connection.")
        print(f"Network error: {str(e)}")
        return None
    except Exception as e:
        speak("I encountered an error while searching. Let me try to fix that.")
        print(f"Error: {str(e)}")
        return None

def set_alarm(time_str, message=""):
    """Set an alarm for a specific time"""
    try:
        alarm_time = datetime.datetime.strptime(time_str, "%H:%M").time()
        current_time = datetime.datetime.now().time()
        
        if alarm_time <= current_time:
            speak("That time has already passed today. Setting alarm for tomorrow.")
            alarm_datetime = datetime.datetime.combine(datetime.datetime.now().date() + datetime.timedelta(days=1), alarm_time)
        else:
            alarm_datetime = datetime.datetime.combine(datetime.datetime.now().date(), alarm_time)
        
        time_difference = (alarm_datetime - datetime.datetime.now()).total_seconds()
        
        if time_difference > 0:
            speak(f"Alarm set for {time_str}. {message}")
            time.sleep(time_difference)
            speak(f"Alarm! {message}")
            # Play alarm sound
            winsound.Beep(1000, 1000)  # 1000 Hz for 1 second
        else:
            speak("Invalid time format. Please use HH:MM format.")
            
    except ValueError:
        speak("Invalid time format. Please use HH:MM format.")
    except Exception as e:
        speak(f"Error setting alarm: {str(e)}")

def take_note():
    """Take a voice note"""
    try:
        speak("What would you like me to note down?")
        note = listen()
        
        if note:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open("notes.txt", "a", encoding="utf-8") as file:
                file.write(f"[{timestamp}] {note}\n")
            speak("Note saved successfully!")
        else:
            speak("I didn't catch that. Please try again.")
            
    except Exception as e:
        speak(f"Error saving note: {str(e)}")

def read_notes():
    """Read all saved notes"""
    try:
        with open("notes.txt", "r", encoding="utf-8") as file:
            notes = file.readlines()
            
        if notes:
            speak("Here are your notes:")
            for note in notes[-5:]:  # Read last 5 notes
                speak(note.strip())
        else:
            speak("You don't have any notes yet.")
            
    except FileNotFoundError:
        speak("You don't have any notes yet.")
    except Exception as e:
        speak(f"Error reading notes: {str(e)}")

def set_timer(seconds):
    """Set a timer for specified seconds"""
    try:
        seconds = int(seconds)
        if seconds <= 0:
            speak("Please specify a positive number of seconds.")
            return
            
        speak(f"Timer set for {seconds} seconds.")
        time.sleep(seconds)
        speak("Time's up!")
        # Play timer sound
        winsound.Beep(2000, 500)  # 2000 Hz for 0.5 seconds
        
    except ValueError:
        speak("Please specify a valid number of seconds.")
    except Exception as e:
        speak(f"Error setting timer: {str(e)}")

def save_learning_data():
    """Save learning data to file"""
    try:
        with open('jarvis_learning.json', 'w') as f:
            json.dump(learning_data, f)
    except Exception as e:
        print(f"Error saving learning data: {str(e)}")

def load_learning_data():
    """Load learning data from file"""
    try:
        with open('jarvis_learning.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return learning_data
    except Exception as e:
        print(f"Error loading learning data: {str(e)}")
        return learning_data

def detect_emotion(text):
    """Enhanced emotion detection using keyword matching and sentiment analysis"""
    emotion_keywords = {
        "happy": ["happy", "joy", "excited", "great", "wonderful", "amazing", "love", "awesome", "fantastic"],
        "sad": ["sad", "unhappy", "depressed", "terrible", "awful", "bad", "upset", "disappointed", "sorry"],
        "angry": ["angry", "mad", "furious", "annoyed", "upset", "frustrated", "irritated", "hate"],
        "fearful": ["scared", "afraid", "worried", "anxious", "nervous", "terrified"],
        "surprised": ["wow", "amazing", "incredible", "unbelievable", "shocked"],
        "neutral": ["okay", "fine", "alright", "normal", "regular", "usual"]
    }
    
    # Convert text to lowercase and remove punctuation
    text = text.lower()
    text = ''.join(c for c in text if c.isalnum() or c.isspace())
    
    # Count emotion keywords
    emotion_counts = {emotion: 0 for emotion in emotion_keywords}
    for emotion, keywords in emotion_keywords.items():
        for keyword in keywords:
            if keyword in text:
                emotion_counts[emotion] += 1
    
    # Determine dominant emotion
    max_count = max(emotion_counts.values())
    if max_count == 0:
        return "neutral"
    
    dominant_emotions = [emotion for emotion, count in emotion_counts.items() if count == max_count]
    
    # If multiple emotions have same count, use context from previous interactions
    if len(dominant_emotions) > 1 and conversation_history:
        last_emotion = conversation_history[-1].get("emotion", "neutral")
        if last_emotion in dominant_emotions:
            return last_emotion
    
    return dominant_emotions[0]

def is_repetitive_command(query):
    """Check if the command is repetitive or too similar to recent commands"""
    global command_history, last_command_time
    
    current_time = time.time()
    query_lower = query.lower().strip()
    
    # Check for exact repetition within last 30 seconds
    for cmd_data in command_history[-5:]:  # Check last 5 commands
        if cmd_data["command"] == query_lower:
            time_diff = current_time - cmd_data["timestamp"]
            if time_diff < 30:  # 30 seconds threshold
                return True, "exact_repeat"
    
    # Check for similar commands (fuzzy matching)
    for cmd_data in command_history[-3:]:  # Check last 3 commands
        if cmd_data["command"] == query_lower:
            time_diff = current_time - cmd_data["timestamp"]
            if time_diff < 60:  # 1 minute threshold for similar commands
                return True, "similar_repeat"
    
    # Check for command frequency (same command type within short time)
    command_type = extract_command_type(query_lower)
    if command_type in last_command_time:
        time_diff = current_time - last_command_time[command_type]
        if time_diff < 10:  # 10 seconds threshold for same command type
            return True, "type_repeat"
    
    return False, None

def extract_command_type(query):
    """Extract the type of command from the query"""
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['time', 'what time', 'current time']):
        return 'time'
    elif any(word in query_lower for word in ['weather', 'temperature', 'forecast']):
        return 'weather'
    elif any(word in query_lower for word in ['news', 'headlines', 'latest news']):
        return 'news'
    elif any(word in query_lower for word in ['open', 'launch', 'start']):
        return 'open_app'
    elif any(word in query_lower for word in ['search', 'look up', 'find']):
        return 'search'
    elif any(word in query_lower for word in ['calculate', 'math', 'compute']):
        return 'calculate'
    elif any(word in query_lower for word in ['play', 'music', 'song']):
        return 'music'
    else:
        return 'general'

def get_varied_response(response_type, **kwargs):
    """Get a varied response to avoid repetition"""
    if response_type in response_variations:
        responses = response_variations[response_type]
        # Use conversation depth to select response
        response_index = conversation_state["conversation_depth"] % len(responses)
        response = responses[response_index]
        
        # Format with provided kwargs
        try:
            return response.format(**kwargs)
        except KeyError:
            return response
    return kwargs.get('default', "I understand.")

def update_conversation_state(query, response_type):
    """Update conversation state to maintain context"""
    global conversation_state, command_history
    
    # Update conversation depth
    conversation_state["conversation_depth"] += 1
    
    # Update current topic based on query
    if 'weather' in query.lower():
        conversation_state["current_topic"] = "weather"
    elif 'time' in query.lower():
        conversation_state["current_topic"] = "time"
    elif 'news' in query.lower():
        conversation_state["current_topic"] = "news"
    elif any(word in query.lower() for word in ['music', 'song', 'play']):
        conversation_state["current_topic"] = "music"
    else:
        conversation_state["current_topic"] = "general"
    
    # Track command history
    command_data = {
        "command": query.lower().strip(),
        "timestamp": time.time(),
        "response_type": response_type
    }
    command_history.append(command_data)
    
    # Keep only last 10 commands
    if len(command_history) > 10:
        command_history = command_history[-10:]
    
    # Update last command time for this type
    command_type = extract_command_type(query.lower())
    last_command_time[command_type] = time.time()

def handle_repetitive_command(query, repeat_type):
    """Handle repetitive commands with appropriate responses"""
    if repeat_type == "exact_repeat":
        responses = [
            "I just told you that. Is there something else I can help you with?",
            
        ]    
    else:
        responses = ["I'm here to help. What else can I assist you with?"]
    
    # Select response based on conversation depth
    response_index = conversation_state["conversation_depth"] % len(responses)
    return responses[response_index]

def reset_conversation_state():
    """Reset conversation state for a fresh start"""
    global conversation_state, command_history, conversation_history, last_command_time
    conversation_state = {
        "current_topic": None,
        "ongoing_task": None,
        "user_mood": "neutral",
        "conversation_depth": 0
    }
    command_history = []
    conversation_history = []
    last_command_time = {}
    speak("Conversation state reset. How can I help you?")

def get_conversation_summary():
    """Get a summary of the current conversation"""
    if not conversation_history:
        return "No conversation history yet."
    
    recent_topics = [item.get("query", "") for item in conversation_history[-3:]]
    return f"Recent topics: {', '.join(recent_topics)}"

def adjust_personality_based_on_context():
    """Adjust personality traits based on conversation context"""
    global learning_data
    
    # Analyze recent interactions
    recent_interactions = conversation_history[-5:] if len(conversation_history) >= 5 else conversation_history
    
    if not recent_interactions:
        return
    
    # Count emotion occurrences
    emotion_counts = {}
    for interaction in recent_interactions:
        emotion = interaction.get("emotion", "neutral")
        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
    
    # Adjust personality based on emotions
    if emotion_counts.get("sad", 0) > 2:
        learning_data["personality"]["traits"]["empathetic"] = min(1.0, learning_data["personality"]["traits"]["empathetic"] + 0.1)
    elif emotion_counts.get("angry", 0) > 2:
        learning_data["personality"]["traits"]["professional"] = min(1.0, learning_data["personality"]["traits"]["professional"] + 0.1)
    elif emotion_counts.get("happy", 0) > 2:
        learning_data["personality"]["traits"]["humorous"] = min(1.0, learning_data["personality"]["traits"]["humorous"] + 0.1)

def get_conversation_style():
    """Determine appropriate conversation style based on context and personality"""
    global learning_data
    
    # Get current time
    current_hour = datetime.datetime.now().hour
    
    # Adjust style based on time of day
    if 6 <= current_hour < 12:
        return "energetic"
    elif 12 <= current_hour < 18:
        return "balanced"
    elif 18 <= current_hour < 22:
        return "casual"
    else:
        return "formal"

def chat_with_ai(query):
    """Enhanced chat with context awareness, personality, and emotion detection"""
    try:
        # Detect emotion from query
        current_emotion = detect_emotion(query)
        
        # Update conversation history
        conversation_history.append({
            "query": query,
            "emotion": current_emotion,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
        # Keep history within window
        if len(conversation_history) > context_window:
            conversation_history = conversation_history[-context_window:]
        
        # Adjust personality based on context
        adjust_personality_based_on_context()
        
        # Get conversation style
        conversation_style = get_conversation_style()
        
        # Prepare context for AI with recent commands to avoid repetition
        recent_commands = [cmd["command"] for cmd in command_history[-3:]]
        context = "\n".join([
            f"Previous query: {item['query']}\nEmotion: {item['emotion']}"
            for item in conversation_history[-3:]
        ])
        
        # Add recent commands context
        if recent_commands:
            context += f"\nRecent commands: {', '.join(recent_commands)}"
        
        # Prepare the API request with enhanced context
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": f"""You are Jarvis, an advanced AI assistant with the following personality traits:
                - Friendliness: {learning_data['personality']['traits']['friendly']}
                - Professionalism: {learning_data['personality']['traits']['professional']}
                - Humor: {learning_data['personality']['traits']['humorous']}
                - Empathy: {learning_data['personality']['traits']['empathetic']}
                
                Current conversation style: {conversation_style}
                User's current emotion: {current_emotion}
                Current topic: {conversation_state['current_topic']}
                Conversation depth: {conversation_state['conversation_depth']}
                
                Previous interactions:
                {context}
                
                IMPORTANT: Avoid repeating information you just provided. If the user asks something similar to recent commands, acknowledge it and offer to elaborate or help with something different. Be conversational and natural while maintaining your personality."""},
                {"role": "user", "content": query}
            ],
            "temperature": 0.7,
            "max_tokens": 200
        }
        
        # Make the API request
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result['choices'][0]['message']['content']
            
            # Update conversation history with response
            conversation_history[-1]["response"] = answer
            
            # Update conversation state
            update_conversation_state(query, "chat")
            
            # Save updated data
            save_learning_data()
            
            return answer
        else:
            return "I'm having trouble processing that right now. Could you please try again?"
            
    except Exception as e:
        print(f"Chat error: {str(e)}")
        return "I encountered an error while processing your request. Let's try again."

def is_conversational(query):
    """Check if the query is conversational"""
    conversation_starters = [
        'let\'s chat',
        'can we talk',
        'want to talk',
        'tell me about yourself',
        'how do you feel',
        'what do you think',
        'do you like',
        'have you ever',
        'what\'s your opinion',
        'tell me more',
        'interesting',
        'really',
        'why do you',
        'that\'s cool',
        'awesome',
        'nice'
    ]
    
    return any(starter in query.lower() for starter in conversation_starters)

def load_smart_home_config():
    """Load smart home configuration from file"""
    try:
        with open('smart_home_config.yaml', 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return SMART_HOME_CONFIG
    except Exception as e:
        print(f"Error loading smart home config: {str(e)}")
        return SMART_HOME_CONFIG

def save_smart_home_config():
    """Save smart home configuration to file"""
    try:
        with open('smart_home_config.yaml', 'w') as f:
            yaml.dump(SMART_HOME_CONFIG, f)
    except Exception as e:
        print(f"Error saving smart home config: {str(e)}")

def initialize_mqtt():
    """Initialize MQTT client for smart home control"""
    try:
        client = mqtt.Client()
        client.connect(SMART_HOME_CONFIG["mqtt_broker"], SMART_HOME_CONFIG["mqtt_port"])
        client.loop_start()
        return client
    except Exception as e:
        print(f"Error initializing MQTT: {str(e)}")
        return None

def control_smart_device(device_name, action):
    """Control a smart home device"""
    try:
        if device_name in SMART_HOME_CONFIG["devices"]:
            device = SMART_HOME_CONFIG["devices"][device_name]
            topic = f"home/{device['room']}/{device_name}/control"
            payload = {"action": action}
            
            mqtt_client = initialize_mqtt()
            if mqtt_client:
                mqtt_client.publish(topic, str(payload))
                speak(f"Controlling {device_name} to {action}")
                return True
        else:
            speak(f"I don't recognize the device {device_name}")
            return False
    except Exception as e:
        print(f"Error controlling device: {str(e)}")
        speak("I had trouble controlling the device")
        return False

def add_smart_device(device_name, room, device_type):
    """Add a new smart home device"""
    try:
        SMART_HOME_CONFIG["devices"][device_name] = {
            "room": room,
            "type": device_type,
            "status": "off"
        }
        save_smart_home_config()
        speak(f"Added {device_name} in {room}")
        return True
    except Exception as e:
        print(f"Error adding device: {str(e)}")
        speak("I had trouble adding the device")
        return False

def create_automation(name, trigger, action):
    """Create a new automation rule"""
    try:
        if "automations" not in SMART_HOME_CONFIG:
            SMART_HOME_CONFIG["automations"] = {}
        
        SMART_HOME_CONFIG["automations"][name] = {
            "trigger": trigger,
            "action": action,
            "enabled": True
        }
        save_smart_home_config()
        speak(f"Created automation rule: {name}")
        return True
    except Exception as e:
        print(f"Error creating automation: {str(e)}")
        speak("I had trouble creating the automation")
        return False

def schedule_task(task_name, schedule_time, action):
    """Schedule a recurring task"""
    try:
        def task_wrapper():
            speak(f"Running scheduled task: {task_name}")
            # Execute the action
            if isinstance(action, str):
                respond(action)
            elif callable(action):
                action()
        
        # Parse schedule time (e.g., "every day at 9:00" or "every hour")
        if "every day at" in schedule_time:
            time_str = schedule_time.split("at")[1].strip()
            schedule.every().day.at(time_str).do(task_wrapper)
        elif "every hour" in schedule_time:
            schedule.every().hour.do(task_wrapper)
        elif "every" in schedule_time and "minutes" in schedule_time:
            minutes = int(schedule_time.split("every")[1].split("minutes")[0].strip())
            schedule.every(minutes).minutes.do(task_wrapper)
        
        speak(f"Scheduled task: {task_name} for {schedule_time}")
        return True
    except Exception as e:
        print(f"Error scheduling task: {str(e)}")
        speak("I had trouble scheduling the task")
        return False

def run_scheduler():
    """Run the task scheduler in a separate thread"""
    def scheduler_loop():
        while True:
            schedule.run_pending()
            time.sleep(1)
    
    scheduler_thread = threading.Thread(target=scheduler_loop)
    scheduler_thread.daemon = True
    scheduler_thread.start()

def initialize_security():
    """Initialize security features"""
    try:
        key_file = 'encryption_key.key'
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                SECURITY_CONFIG["encryption_key"] = f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            SECURITY_CONFIG["encryption_key"] = key
        
        # Load authorized users
        try:
            with open('authorized_users.json', 'r') as f:
                SECURITY_CONFIG["authorized_users"] = json.load(f)
        except FileNotFoundError:
            SECURITY_CONFIG["authorized_users"] = {}
        
        return True
    except Exception as e:
        print(f"Security initialization error: {str(e)}")
        return False

def encrypt_data(data):
    """Encrypt sensitive data"""
    try:
        f = Fernet(SECURITY_CONFIG["encryption_key"])
        return f.encrypt(data.encode()).decode()
    except Exception as e:
        print(f"Encryption error: {str(e)}")
        return None

def decrypt_data(encrypted_data):
    """Decrypt sensitive data"""
    try:
        f = Fernet(SECURITY_CONFIG["encryption_key"])
        return f.decrypt(encrypted_data.encode()).decode()
    except Exception as e:
        print(f"Decryption error: {str(e)}")
        return None

def authenticate_user(voice_sample):
    """Authenticate user using voice biometrics"""
    try:
        if not SECURITY_CONFIG["voice_auth_enabled"]:
            return True  # Skip authentication if not enabled
        
        # Convert voice sample to hash
        voice_hash = hashlib.sha256(voice_sample.encode()).hexdigest()
        
        # Check against authorized users
        for user, stored_hash in SECURITY_CONFIG["authorized_users"].items():
            if voice_hash == stored_hash:
                return True
        
        return False
    except Exception as e:
        print(f"Authentication error: {str(e)}")
        return False

def add_authorized_user(username, voice_sample):
    """Add a new authorized user"""
    try:
        voice_hash = hashlib.sha256(voice_sample.encode()).hexdigest()
        SECURITY_CONFIG["authorized_users"][username] = voice_hash
        
        # Save authorized users
        with open('authorized_users.json', 'w') as f:
            json.dump(SECURITY_CONFIG["authorized_users"], f)
        
        return True
    except Exception as e:
        print(f"Error adding authorized user: {str(e)}")
        return False

def system_control(action):
    """Control system operations like shutdown, restart, lock screen"""
    try:
        if action == "shutdown":
            speak("Shutting down the computer in 10 seconds. Press Ctrl+C to cancel.")
            time.sleep(10)
            os.system("shutdown /s /t 0")
        elif action == "restart":
            speak("Restarting the computer in 10 seconds. Press Ctrl+C to cancel.")
            time.sleep(10)
            os.system("shutdown /r /t 0")
        elif action == "lock":
            os.system("rundll32.exe user32.dll,LockWorkStation")
            speak("Screen locked")
        elif action == "sleep":
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            speak("Putting computer to sleep")
        elif action == "hibernate":
            os.system("shutdown /h")
            speak("Hibernating computer")
        elif action == "logoff":
            os.system("shutdown /l")
            speak("Logging off user")
        else:
            speak(f"Unknown system action: {action}")
            return False
        return True
    except Exception as e:
        speak(f"Error performing system action: {str(e)}")
        return False

def close_application(app_name):
    """Close a specific application"""
    try:
        if app_name.lower() in ["all", "everything"]:
            os.system("taskkill /f /im *")
            speak("Closing all applications")
        else:
            # Try to close by process name
            os.system(f"taskkill /f /im {app_name}.exe")
            speak(f"Closing {app_name}")
        return True
    except Exception as e:
        speak(f"Error closing application: {str(e)}")
        return False

def file_operations(operation, path=None, name=None):
    """Perform file and folder operations"""
    try:
        if operation == "create_folder" and name:
            os.makedirs(name, exist_ok=True)
            speak(f"Created folder: {name}")
        elif operation == "delete_file" and path:
            if os.path.exists(path):
                os.remove(path)
                speak(f"Deleted file: {path}")
            else:
                speak("File not found")
        elif operation == "create_file" and name:
            with open(name, 'w') as f:
                f.write("")
            speak(f"Created file: {name}")
        elif operation == "list_files" and path:
            files = os.listdir(path)
            speak(f"Found {len(files)} items in {path}")
            for file in files[:5]:  # List first 5 files
                speak(file)
        else:
            speak(f"Unknown file operation: {operation}")
            return False
        return True
    except Exception as e:
        speak(f"Error performing file operation: {str(e)}")
        return False

def network_operations(operation):
    """Perform network-related operations"""
    try:
        if operation == "check_internet":
            try:
                requests.get("http://www.google.com", timeout=5)
                speak("Internet connection is working")
            except:
                speak("No internet connection")
        elif operation == "ip_address":
            import socket
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            speak(f"Your IP address is {ip}")
        elif operation == "wifi_info":
            result = subprocess.run(["netsh", "wlan", "show", "profiles"], capture_output=True, text=True)
            speak("WiFi information retrieved")
        else:
            speak(f"Unknown network operation: {operation}")
            return False
        return True
    except Exception as e:
        speak(f"Error performing network operation: {str(e)}")
        return False

# Initialize MediaPipe for gesture recognition
# mp_hands = mp.solutions.hands
# hands = mp_hands.Hands(
#     static_image_mode=False,
#     max_num_hands=2,
#     min_detection_confidence=0.5
# )

def detect_gestures():
    """Detect hand gestures using webcam"""
    try:
        cap = cv2.VideoCapture(0)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Convert the BGR image to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process the frame and detect hands
            # results = hands.process(rgb_frame)
            
            # if results.multi_hand_landmarks:
            #     for hand_landmarks in results.multi_hand_landmarks:
            #         # Draw hand landmarks
            #         mp.solutions.drawing_utils.draw_landmarks(
            #             frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    
            #         # Detect specific gestures
            #         # Example: Thumbs up
            #         thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            #         if thumb_tip.y < hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y:
            #             return "thumbs_up"
            
            cv2.imshow('Gesture Detection', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        return None
    except Exception as e:
        print(f"Gesture detection error: {str(e)}")
        return None

def handle_gesture(gesture):
    """Handle detected gestures"""
    try:
        if gesture == "thumbs_up":
            speak("I see you're giving a thumbs up!")
            return True
        return False
    except Exception as e:
        print(f"Gesture handling error: {str(e)}")
        return False

def start_gesture_detection():
    """Start gesture detection in a separate thread"""
    def gesture_loop():
        while True:
            gesture = detect_gestures()
            if gesture:
                handle_gesture(gesture)
            time.sleep(0.1)
    
    gesture_thread = threading.Thread(target=gesture_loop)
    gesture_thread.daemon = True
    gesture_thread.start()

def respond(query):
    global user_name
    
    if query == "":
        return True
    
    # Check for repetitive commands first
    is_repetitive, repeat_type = is_repetitive_command(query)
    if is_repetitive:
        response = handle_repetitive_command(query, repeat_type)
        speak(response)
        update_conversation_state(query, "repetitive_response")
        return True
    
    # Security check
    if not authenticate_user(query):
        speak("I'm sorry, I couldn't verify your identity.")
        return False
    
    # Gesture commands
    if 'start gesture detection' in query:
        start_gesture_detection()
        speak("Gesture detection started")
        return True
    
    elif 'add authorized user' in query:
        parts = query.split('add authorized user')
        if len(parts) == 2:
            username = parts[1].strip()
            speak("Please say something for voice authentication")
            voice_sample = listen()
            if voice_sample:
                add_authorized_user(username, voice_sample)
                speak(f"Added {username} as an authorized user")
                return True
    
    # Load configurations
    global SMART_HOME_CONFIG
    SMART_HOME_CONFIG = load_smart_home_config()
    
    # Smart Home Commands
    if 'control' in query and 'to' in query:
        # Extract device and action
        parts = query.split('control')[1].split('to')
        if len(parts) == 2:
            device = parts[0].strip()
            action = parts[1].strip()
            control_smart_device(device, action)
            return True
    
    elif 'add device' in query:
        # Extract device details
        parts = query.split('add device')[1].split('in')
        if len(parts) == 2:
            device_name = parts[0].strip()
            room = parts[1].strip()
            add_smart_device(device_name, room, "generic")
            return True
    
    elif 'create automation' in query:
        # Extract automation details
        parts = query.split('create automation')[1].split('when')
        if len(parts) == 2:
            name = parts[0].strip()
            trigger_action = parts[1].split('then')
            if len(trigger_action) == 2:
                trigger = trigger_action[0].strip()
                action = trigger_action[1].strip()
                create_automation(name, trigger, action)
                return True
    
    elif 'schedule task' in query:
        # Extract task details
        parts = query.split('schedule task')[1].split('for')
        if len(parts) == 2:
            task_name = parts[0].strip()
            schedule_time = parts[1].strip()
            schedule_task(task_name, schedule_time, lambda: speak(f"Running scheduled task: {task_name}"))
            return True
    
    # Load learning data at start
    global learning_data
    learning_data = load_learning_data()
    
    # Handle conversational queries with enhanced features
    if is_conversational(query):
        chat_with_ai(query)
        return True
    
    # Calculation commands
    elif 'calculate' in query or 'what is' in query:
        # Extract the calculation expression
        expression = query.replace('calculate', '').replace('what is', '').strip()
        calculate(expression)
    
    # AI Search command
    elif 'search on ai' in query or 'ask ai' in query:
        # Extract the search query
        search_match = re.search(r'(?:search on ai|ask ai) (.*?)(?:\s|$)', query)
        if search_match:
            search_query = search_match.group(1)
            speak(f"I'll search for information about {search_query}")
            ai_search(search_query)
        else:
            speak("What would you like me to search for?")
            search_query = listen()
            if search_query != "":
                speak(f"I'll search for information about {search_query}")
                ai_search(search_query)
    
    # Voice commands
    elif 'change voice' in query:
        if 'female' in query:
            change_voice("female", current_rate)
        elif 'male' in query:
            change_voice("male", current_rate)
        elif 'list' in query or 'show' in query:
            list_voices()
        else:
            speak("Please specify 'male' or 'female' voice, or say 'list voices' to see available options")
    
    # English greetings
    elif 'hello' in query or 'hi' in query:
        response = get_varied_response("greeting")
        speak(response)
        update_conversation_state(query, "greeting")
    
    elif 'how are you' in query:
        speak("I'm doing great! How about you?")
        update_conversation_state(query, "greeting")
    
    elif 'time' in query:
        current_time = datetime.datetime.now().strftime("%H:%M")
        response = get_varied_response("time", time=current_time)
        speak(response)
        update_conversation_state(query, "time")
    
    elif 'date' in query:
        date = datetime.datetime.now().strftime("%d %B %Y")
        speak(f"Today's date is {date}")
        update_conversation_state(query, "date")
    
    elif 'thank you' in query:
        speak("You're welcome!")
        update_conversation_state(query, "acknowledgment")
    
    # Enhanced exit commands
    elif any(exit_word in query.lower() for exit_word in [
        'bye', 'goodbye', 'see you later', 'catch you later', 'farewell',
        'turn off', 'shutdown', 'power down', 'exit', 'quit', 'stop',
        'end session', 'close jarvis', 'deactivate', 'disconnect',
        'sleep mode', 'hibernate', 'standby', 'shut down jarvis',
        'turn off jarvis', 'good night', 'see you tomorrow',
        'adios', 'ciao', 'later', 'take care', 'see ya', 'peace out',
        'sign off', 'log off', 'terminate', 'finish', 'done', 'complete',
        'shut down', 'power off', 'turn off jarvis', 'close jarvis',
        'end jarvis', 'stop jarvis', 'quit jarvis', 'exit jarvis'
    ]):
        farewell_responses = [
            f"Goodbye {user_name}! Have a great day!",
            f"See you later {user_name}! Take care!",
            f"Farewell {user_name}! Until next time!",
            f"Goodbye {user_name}! It was great talking with you!",
            f"See you soon {user_name}! Stay awesome!",
            f"Take care {user_name}! Have a wonderful day!",
            f"Goodbye {user_name}! I'll be here whenever you need me!",
            f"See you later {user_name}! Stay productive!"
        ]
        
        # Select farewell response based on time of day
        current_hour = datetime.datetime.now().hour
        if 6 <= current_hour < 12:
            response = f"Good morning {user_name}! Have a great day ahead!"
        elif 12 <= current_hour < 18:
            response = f"Good afternoon {user_name}! Take care!"
        elif 18 <= current_hour < 22:
            response = f"Good evening {user_name}! Have a wonderful night!"
        else:
            response = f"Good night {user_name}! Sweet dreams!"
        
        speak(response)
        update_conversation_state(query, "farewell")
        return False  # This is crucial for actually exiting the program
    
    # Weather
    elif 'weather' in query:
        city_match = re.search(r'weather in (.*?)(?:\s|$)', query)
        if city_match:
            city = city_match.group(1)
            weather_info = get_weather(city)
            if weather_info:
                update_conversation_state(query, "weather")
        else:
            weather_info = get_weather()
            if weather_info:
                update_conversation_state(query, "weather")
    
    # News
    elif 'news' in query:
        category_match = re.search(r'news about (.*?)(?:\s|$)', query)
        if category_match:
            category = category_match.group(1)
            get_news(category)
        else:
            get_news()
    
    # System stats
    elif 'system' in query and ('stats' in query or 'status' in query):
        system_stats()
    
    # Reminders
    elif 'remind me' in query:
        time_match = re.search(r'at (\d{1,2}:\d{2})', query)
        if time_match:
            time_str = time_match.group(1)
            message_match = re.search(r'to (.*?)(?:\s|$)', query)
            if message_match:
                message = message_match.group(1)
                set_reminder(time_str, message)
            else:
                speak("What should I remind you about?")
                message = listen()
                if message != "":
                    set_reminder(time_str, message)
        else:
            speak("What time should I remind you?")
            time_query = listen()
            if time_query != "":
                time_match = re.search(r'(\d{1,2}:\d{2})', time_query)
                if time_match:
                    time_str = time_match.group(1)
                    speak("What should I remind you about?")
                    message = listen()
                    if message != "":
                        set_reminder(time_str, message)
                else:
                    speak("I couldn't understand the time. Please use format HH:MM")
    
    # Web search
    elif 'search' in query or 'look up' in query:
        search_match = re.search(r'(?:search for|look up) (.*?)(?:\s|$)', query)
        if search_match:
            search_query = search_match.group(1)
            web_search(search_query)
        else:
            speak("What would you like me to search for?")
            search_query = listen()
            if search_query != "":
                web_search(search_query)
    
    # Email
    elif 'send email' in query:
        speak("Who should I send the email to?")
        to_email = listen()
        if to_email != "":
            speak("What should be the subject?")
            subject = listen()
            if subject != "":
                speak("What should be the message?")
                body = listen()
                if body != "":
                    send_email(to_email, subject, body)
    
    # Music
    elif 'play music' in query or 'play song' in query:
        # Extract the song name
        song_match = re.search(r'(?:play music|play song) (.*?)(?:\s|$)', query)
        if song_match:
            song_name = song_match.group(1)
            play_music(song_name)
        else:
            speak("What song would you like me to play?")
            song_name = listen()
            if song_name != "":
                play_music(song_name)
    
    # Screenshot
    elif 'take screenshot' in query:
        take_screenshot()
    
    # Open websites
    elif 'open youtube' in query:
        open_website("https://www.youtube.com", "YouTube")
    
    elif 'open google' in query:
        open_website("https://www.google.com", "Google")
    
    elif 'open gmail' in query:
        open_website("https://mail.google.com", "Gmail")
    
    elif 'open facebook' in query:
        open_website("https://www.facebook.com", "Facebook")
    
    elif 'open twitter' in query:
        open_website("https://twitter.com", "Twitter")
    
    elif 'open instagram' in query:
        open_website("https://www.instagram.com", "Instagram")
    
    elif 'open linkedin' in query:
        open_website("https://www.linkedin.com", "LinkedIn")
    
    elif 'open amazon' in query:
        open_website("https://www.amazon.com", "Amazon")
    
    elif 'open netflix' in query:
        open_website("https://www.netflix.com", "Netflix")
    
    elif 'open spotify' in query:
        open_website("https://open.spotify.com", "Spotify")
    
    elif 'open github' in query:
        open_website("https://github.com", "GitHub")
    
    # Enhanced application opening
    elif 'open notepad' in query:
        open_application("notepad")
        update_conversation_state(query, "notepad.exe")
    
    elif 'open calculator' in query:
        open_application("calculator")
        update_conversation_state(query, "calculator.exe")
    
    elif 'open paint' in query:
        open_application("paint")
        update_conversation_state(query, "paint.exe")
    
    elif 'open word' in query:
        open_application("word")
        update_conversation_state(query, "word.exe")
    
    elif 'open excel' in query:
        open_application("excel")
        update_conversation_state(query, "excel.exe")
    
    elif 'open powerpoint' in query:
        open_application("powerpoint")
        update_conversation_state(query, "powerpoint.exe")
    
    elif 'open chrome' in query:
        open_application("chrome")
        update_conversation_state(query, "chrome.exe")
    
    elif 'open explorer' in query:
        open_application("explorer")
        update_conversation_state(query, "explorer.exe")
    
    # New system applications
    elif 'open task manager' in query:
        open_application("task manager")
        update_conversation_state(query, "task manager.exe")
    
    elif 'open control panel' in query:
        open_application("control panel")
        update_conversation_state(query, "control panel.exe")
    
    elif 'open settings' in query:
        open_application("settings")
        update_conversation_state(query, "settings.exe")
    
    elif 'open command prompt' in query:
        open_application("command prompt")
        update_conversation_state(query, "command prompt.exe")
    
    elif 'open powershell' in query:
        open_application("powershell")
        update_conversation_state(query, "powershell.exe")
    
    # System control commands
    elif any(word in query.lower() for word in ['shutdown', 'shut down', 'turn off computer']):
        system_control("shutdown")
        update_conversation_state(query, "system_control")
    
    elif any(word in query.lower() for word in ['restart', 'reboot', 'restart computer']):
        system_control("restart")
        update_conversation_state(query, "system_control")
    
    elif any(word in query.lower() for word in ['lock screen', 'lock computer', 'lock']):
        system_control("lock")
        update_conversation_state(query, "system_control")
    
    elif any(word in query.lower() for word in ['sleep', 'sleep mode', 'put to sleep']):
        system_control("sleep")
        update_conversation_state(query, "system_control")
    
    elif any(word in query.lower() for word in ['hibernate', 'hibernation']):
        system_control("hibernate")
        update_conversation_state(query, "system_control")
    
    # Application closing commands
    elif 'close' in query and ('application' in query or 'app' in query):
        app_match = re.search(r'close (.*?)(?:\s|$)', query)
        if app_match:
            app_name = app_match.group(1)
            close_application(app_name)
        else:
            speak("Which application would you like me to close?")
        update_conversation_state(query, "app_close.exe")
    
    # File operations
    elif 'create folder' in query:
        folder_match = re.search(r'create folder (.*?)(?:\s|$)', query)
        if folder_match:
            folder_name = folder_match.group(1)
            file_operations("create_folder", name=folder_name)
        else:
            speak("What would you like to name the folder?")
        update_conversation_state(query, "file_operation")
    
    elif 'create file' in query:
        file_match = re.search(r'create file (.*?)(?:\s|$)', query)
        if file_match:
            file_name = file_match.group(1)
            file_operations("create_file", name=file_name)
        else:
            speak("What would you like to name the file?")
        update_conversation_state(query, "file_operation")
    
    # Network operations
    elif 'check internet' in query or 'internet connection' in query:
        network_operations("check_internet")
        update_conversation_state(query, "network_operation")
    
    elif 'ip address' in query or 'my ip' in query:
        network_operations("ip_address")
        update_conversation_state(query, "network_operation")
    
    elif 'wifi info' in query or 'wifi information' in query:
        network_operations("wifi_info")
        update_conversation_state(query, "network_operation")
    
    # Enhanced help command
    elif 'help' in query or 'what can you do' in query:
        speak("I can help you with the following categories:")
        speak("APPLICATIONS: Open Notepad, Calculator, Paint, Word, Excel, PowerPoint, Chrome, File Explorer, Task Manager, Control Panel, Settings, Command Prompt, PowerShell")
        speak("WEBSITES: Open YouTube, Google, Gmail, Facebook, Twitter, Instagram, LinkedIn, Amazon, Netflix, Spotify, GitHub, and many more")
        speak("SYSTEM CONTROL: Shutdown, restart, lock screen, sleep, hibernate, log off your computer")
        speak("FILE OPERATIONS: Create folders and files, delete files, organize your desktop")
        speak("NETWORK: Check internet connection, get IP address, WiFi information")
        speak("PRODUCTIVITY: Set reminders, alarms, timers, take notes, manage tasks")
        speak("COMMUNICATION: Send emails, make calls, schedule meetings")
        speak("ENTERTAINMENT: Play music, tell jokes, share facts, take screenshots")
        speak("INFORMATION: Weather, news, time, date, system status")
        speak("VOICE CONTROL: Enhanced voice recognition with wake words like 'Hey Jarvis'")
        speak("EXIT COMMANDS: Say 'goodbye', 'turn off', 'shutdown', 'see you later', or 'bye' to exit")
        speak("Just ask me anything or say 'help' for more specific information!")
        update_conversation_state(query, "help")
    
    # Conversation management commands
    elif 'reset conversation' in query or 'start fresh' in query:
        reset_conversation_state()
        return True
    
    elif 'conversation summary' in query or 'what did we talk about' in query:
        summary = get_conversation_summary()
        speak(summary)
        update_conversation_state(query, "summary")
    
    # New functionality commands
    elif 'set alarm' in query:
        time_match = re.search(r'at (\d{1,2}:\d{2})', query)
        if time_match:
            time_str = time_match.group(1)
            message_match = re.search(r'for (.*?)(?:\s|$)', query)
            message = message_match.group(1) if message_match else ""
            set_alarm(time_str, message)
        else:
            speak("What time should I set the alarm for?")
            time_query = listen()
            if time_query:
                time_match = re.search(r'(\d{1,2}:\d{2})', time_query)
                if time_match:
                    time_str = time_match.group(1)
                    speak("What should I remind you about?")
                    message = listen()
                    set_alarm(time_str, message)
                else:
                    speak("Please specify time in HH:MM format")
    
    elif 'take note' in query or 'make a note' in query:
        take_note()
    
    elif 'read notes' in query or 'show notes' in query:
        read_notes()
    
    elif 'set timer' in query:
        seconds_match = re.search(r'for (\d+) seconds?', query)
        if seconds_match:
            seconds = seconds_match.group(1)
            set_timer(seconds)
        else:
            speak("For how many seconds?")
            seconds_query = listen()
            if seconds_query:
                seconds_match = re.search(r'(\d+)', seconds_query)
                if seconds_match:
                    set_timer(seconds_match.group(1))
                else:
                    speak("Please specify a number of seconds")
    
    # For any unrecognized command or question, use chat instead of AI search
    else:
        # Check if it's a question or looks like a question
        if query.endswith('?') or any(word in query.lower() for word in ['what', 'how', 'why', 'when', 'where', 'who', 'which', 'can you', 'tell me about', 'explain']):
            ai_search(query)
        else:
            # For anything else, treat it as a conversation
            chat_with_ai(query)
    
    return True

if __name__ == "__main__":
    try:
        wishMe()
        running = True
        while running:
            query = listen()
            running = respond(query)
    except KeyboardInterrupt:
        print("\nExiting Jarvis...")
        sys.exit(0) 