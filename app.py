from flask import Flask, request, jsonify, render_template, send_from_directory, redirect, url_for
import os
from pathlib import Path
from dotenv import load_dotenv
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.twiml.messaging_response import MessagingResponse
import json

# Load environment variables
load_dotenv()

# Import configuration
import config

# Import chatbot components
from chatbot import KnowledgeBase, ChatService, VoiceService

# Initialize Flask app
app = Flask(__name__)

# Initialize knowledge base
knowledge_base = KnowledgeBase(
    data_dir=config.DATA_DIR,
    vector_store_dir=config.VECTOR_STORE_DIR,
    openai_api_key=config.OPENAI_API_KEY
)

# Load or create vector store
try:
    vector_store = knowledge_base.create_or_load_vector_store()
except Exception as e:
    print(f"Error initializing vector store: {str(e)}")
    print("Will attempt to create vector store on first query")
    vector_store = None

# Initialize chat service
chat_service = ChatService(
    knowledge_base=knowledge_base,
    openai_api_key=config.OPENAI_API_KEY
)

# Initialize voice service
voice_service = VoiceService(
    api_key=config.ELEVENLABS_API_KEY,
    voice_id=config.ELEVENLABS_VOICE_ID,
    cache_dir=config.AUDIO_CACHE_DIR
)

# Routes
@app.route('/')
def index():
    """Render the main chat interface."""
    return render_template('index.html', 
                          categories=config.QUICK_ACCESS_CATEGORIES,
                          twilio_phone=config.TWILIO_PHONE_NUMBER)

@app.route('/about')
def about():
    """Render the about page."""
    return render_template('about.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat API requests."""
    data = request.json
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    
    # Get response from chat service
    response_data = chat_service.get_response(user_message)
    
    return jsonify(response_data)

@app.route('/api/quick-access/<category>', methods=['GET'])
def quick_access(category):
    """Handle quick access requests."""
    # Create a query based on the category
    if category == "Admission Process":
        query = "What is the admission process at Pune University?"
    elif category == "Exam Schedule":
        query = "Tell me about the exam schedule at Pune University."
    elif category == "Fee Structure":
        query = "What is the fee structure at Pune University?"
    elif category == "Scholarship Info":
        query = "What scholarships are available at Pune University?"
    else:
        return jsonify({"error": "Invalid category"}), 400
    
    # Get response from chat service
    response_data = chat_service.get_response(query)
    
    return jsonify(response_data)

@app.route('/api/resources')
def resources():
    """Return a list of available resources."""
    resources_list = [
        {"title": "University Website", "url": "http://www.unipune.ac.in/"},
        {"title": "Academic Calendar", "url": "http://www.unipune.ac.in/university_files/academic_calender.htm"},
        {"title": "Examination Department", "url": "http://exam.unipune.ac.in/"},
        {"title": "University Library", "url": "https://lib.unipune.ac.in/"},
        {"title": "Student Portal", "url": "https://sim.unipune.ac.in/SIM_APP//"},
        {"title": "Admission Portal", "url": "https://campus.unipune.ac.in/"},
        {"title": "Online Fee Payment", "url": "https://campus.unipune.ac.in/"},
        {"title": "Placement Cell", "url": "http://www.unipune.ac.in/dept/science/computer_science/cs_webfiles/place_cells.htm"},
        {"title": "Research Portal", "url": "http://www.unipune.ac.in/research/"},
        {"title": "Hostel Information", "url": "http://www.unipune.ac.in/university_files/hostel_details.htm"},
        {"title": "Health Center", "url": "https://app1.unipune.ac.in/HealthCentre/default.htm"},
        {"title": "International Students Centre", "url": "http://www.unipune.ac.in/university_files/international_centre.htm"},
        {"title": "E-Learning Resources", "url": "http://www.unipune.ac.in/university_files/e-learning.htm"},
        {"title": "Student Welfare", "url": "http://www.unipune.ac.in/other_academic_and_service_units/board_students_welfare/default.htm"}
    ]
    return jsonify(resources_list)

@app.route('/api/notifications')
def notifications():
    """Return a list of notifications."""
    # In a real application, these would come from a database
    notifications_list = [
        ]
    return jsonify(notifications_list)

@app.route('/api/speak', methods=['POST'])
def speak():
    """Convert text to speech and return audio URL."""
    data = request.json
    text = data.get('text', '')
    
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    # Convert text to speech
    audio_url = voice_service.text_to_speech_for_twilio(text)
    
    if audio_url:
        return jsonify({"audio_url": audio_url})
    else:
        return jsonify({"error": "Failed to convert text to speech"}), 500

@app.route('/api/sms', methods=['POST'])
def sms():
    """Handle incoming SMS messages."""
    # Get the message content
    incoming_msg = request.form.get('Body', '').strip()
    
    # Create Twilio response
    resp = MessagingResponse()
    
    # Get response from chat service
    response_text = chat_service.get_response_for_sms(incoming_msg)
    
    # Add message to response
    resp.message(response_text)
    
    return str(resp)

@app.route('/api/voice/welcome', methods=['POST'])
def voice_welcome():
    """Handle incoming voice calls."""
    response = VoiceResponse()
    
    # Add a welcome message
    response.say(
        "Welcome to Pune University Support Hub. Please ask your question after the beep.",
        voice="female"
    )
    
    # Gather speech input
    gather = Gather(
        input='speech',
        action='/api/voice/process',
        method='POST',
        speechTimeout='auto',
        language='en-IN'
    )
    response.append(gather)
    
    # If user doesn't say anything
    response.say("We didn't receive any input. Goodbye!", voice="female")
    
    return str(response)

@app.route('/api/voice/process', methods=['POST'])
def voice_process():
    """Process speech input from voice call."""
    # Get speech input
    speech_result = request.form.get('SpeechResult', '')
    
    # Create Twilio response
    response = VoiceResponse()
    
    if speech_result:
        # Get response from chat service
        chat_response = chat_service.get_response(speech_result)
        response_text = chat_response["response"]
        
        # Generate voice response
        audio_url = voice_service.text_to_speech_for_twilio(response_text)
        
        if audio_url:
            # Play the generated audio
            response.play(audio_url)
        else:
            # Fallback to TTS if audio generation fails
            response.say(response_text, voice="female")
        
        # Ask if user wants to ask another question
        gather = Gather(
            input='speech',
            action='/api/voice/process',
            method='POST',
            speechTimeout='auto',
            language='en-IN'
        )
        gather.say("Do you have another question? If so, please ask after the beep.", voice="female")
        response.append(gather)
        
        # If no response after gather
        response.say("Thank you for using Pune University Support Hub. Goodbye!", voice="female")
    else:
        # If no speech was detected
        response.say("I'm sorry, I couldn't understand what you said. Goodbye!", voice="female")
    
    return str(response)

@app.route('/static/audio_cache/<filename>')
def serve_audio(filename):
    """Serve audio files from the cache directory."""
    return send_from_directory(config.AUDIO_CACHE_DIR, filename)

# Run the app
if __name__ == '__main__':
    app.run(debug=config.DEBUG, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))