## channel.py - a topic-based message channel with filtering and auto-responses

from flask import Flask, request, render_template, jsonify
import json
import requests
from datetime import datetime
from better_profanity import profanity
from flask_cors import CORS
# Flask app setup
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# Configuration
HUB_URL = 'http://vm146.rz.uni-osnabrueck.de/hub'
HUB_AUTHKEY = 'Crr-K24d-2N'
CHANNEL_AUTHKEY = '0987654321'
CHANNEL_NAME = "AI & Tech Chat"  # New topic-based channel name
CHANNEL_TOPIC = "Discuss AI, technology, and coding!"  # Topic description
CHANNEL_ENDPOINT = "http://vm146.rz.uni-osnabrueck.de/u035/"
CHANNEL_FILE = 'messages.json'
CHANNEL_TYPE_OF_SERVICE = 'aiweb24:chat'
MESSAGE_LIMIT = 50  # Store only the last 50 messages
AUTO_RESPONSES = {
    "AI": [
        "Artificial Intelligence is revolutionizing the world! What are your thoughts?",
        "AI is advancing fast—do you think it will replace jobs?",
        "Have you ever used AI tools like ChatGPT or Midjourney?"
    ],
    "machine learning": [
        "Machine learning enables systems to learn from data. Have you used ML before?",
        "ML powers things like recommendation systems and self-driving cars!"
    ],
    "Python": [
        "Python is a great language for AI development. What projects are you working on?",
        "Python is widely used in AI and data science. Have you tried TensorFlow or PyTorch?"
    ]
}

# Function to check authorization headers
def check_authorization(request):
    if 'Authorization' not in request.headers:
        print("❌ Missing authorization header")
        return False
    if request.headers['Authorization'] != 'authkey ' + CHANNEL_AUTHKEY:
        print("❌ Invalid authorization key")
        return False
    return True

# Load existing messages from file
def read_messages():
    try:
        with open(CHANNEL_FILE, 'r') as f:
            messages = json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        messages = []

    # Ensure the welcome message is always there
    if not messages:
        messages.append({
            "content": f"Welcome to {CHANNEL_NAME}! {CHANNEL_TOPIC}",
            "sender": "System",
            "timestamp": datetime.utcnow().isoformat(),
            "extra": None
        })
    return messages

# Save messages to file (ensures only the last 50 messages are stored)
def save_messages(messages):
    messages = messages[-MESSAGE_LIMIT:]  # Keep only the last 50 messages
    with open(CHANNEL_FILE, 'w') as f:
        json.dump(messages, f)

# Register the channel with the hub
@app.cli.command('register')
def register_command():
    """Registers the channel with the hub."""
    response = requests.post(
        HUB_URL + '/channels',
        headers={'Authorization': 'authkey ' + HUB_AUTHKEY},
        json={
            "name": CHANNEL_NAME,
            "endpoint": CHANNEL_ENDPOINT,
            "authkey": CHANNEL_AUTHKEY,
            "type_of_service": CHANNEL_TYPE_OF_SERVICE
        }
    )

    if response.status_code == 200:
        print("✅ Channel registered successfully!")
    else:
        print(f"❌ Error registering channel: {response.status_code}")
        print(response.text)

# Health check route
@app.route('/health', methods=['GET'])
def health_check():
    if not check_authorization(request):
        return "Invalid authorization", 400
    return jsonify({'name': CHANNEL_NAME}), 200

# Home page (renders home.html)
@app.route("/", methods=["GET"])
def home_page():
    return render_template("home.html")

# GET: Return list of messages in a clean HTML page
@app.route('/messages', methods=['GET'])
@app.route('/messages', methods=['GET'])
def get_messages():
    messages = read_messages()
    return jsonify(messages)  # ✅ This ensures proper JSON output


# POST: Send a message
@app.route('/send', methods=['POST'])
def send_message():
    """Handles incoming messages."""
    if not check_authorization(request):
        return "Invalid authorization", 400

    # Parse message
    data = request.json
    content = data.get("content", "")
    sender = data.get("sender", "Anonymous")
    timestamp = data.get("timestamp", datetime.utcnow().isoformat())
    extra = data.get("extra", None)

    if not content or not sender:
        return "Invalid message format", 400

    # Filter unwanted messages
    filtered_content = profanity.censor(content)

    # Add message to store
    messages = read_messages()
    messages.append({
        "content": filtered_content,
        "sender": sender,
        "timestamp": timestamp,
        "extra": extra
    })
    save_messages(messages)

    # Auto-response if needed
    for trigger, responses in AUTO_RESPONSES.items():
        if trigger.lower() in content.lower():
            from random import choice
            bot_message = {
                "content": choice(responses),  # Randomized bot response
                "sender": "AIBot",
                "timestamp": datetime.utcnow().isoformat(),
                "extra": None
            }
            messages.append(bot_message)
            save_messages(messages)
            print(f"🤖 Auto-response triggered for '{trigger}'")

    return "OK", 200

# Help page to display available API routes
@app.route("/help", methods=["GET"])
def help_page():
    return jsonify({
        "Welcome": f"Welcome to {CHANNEL_NAME}! This is a chat about AI and Technology.",
        "Endpoints": {
            "/": "Home page",
            "/messages": "See the list of recent messages",
            "/send": "POST a message (must include 'Authorization' header)",
            "/health": "Check if the server is running",
            "/help": "View this help page"
        }
    })

# Run Flask server
if __name__ == '_main_':
    app.run(port=5001, debug=True)
