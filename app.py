from flask import Flask, request, session
from datetime import datetime
from firebaseAdmin import db
from dotenv import load_dotenv
import os
import whisper
import requests
import hashlib

# Initialize Flask app
app = Flask(__name__)

load_dotenv('./.secrets/.env')
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# Load the Whisper model.
whisperModel = whisper.load_model('small')

def sendDataToTypesense(jsonData):
    headers = {'X-Typesense-Api-Key': os.getenv('TYPESENSE_API_KEY')}
    response = requests.post('https://i3nbyhgz42t1o9vjp-1.a1.typesense.net/collections/transcriptions/documents/import?action=create', headers=headers, json=jsonData)
    return True

def addTranscriptionToFirestore(textRes):
    doc_reference = db.collection(u'users').document('1').collection(u'transcriptions').document()
    data = {}
    data['date_time'] = datetime.now().strftime('%Y-%m-%d %H:%M')
    data['text'] = textRes
    doc_reference.set(data)
    sendDataToTypesense(data)
    return True

# Twilio webhook endpoint
@app.route('/webhook', methods=['POST'])
def handle_webhook():
    # Get the incoming message data from the request
    data = request.form
    message_sid = data.get('MessageSid')
    message_body = data.get('Body')
    from_number = data.get('From')

    # Download from mediaUrl and save to audio_files directory.
        

    # Transcribe the audio file
    transcription = whisperModel.transcribe('audio_files/' + message_sid + '.wav')
    textRes = transcription['text']
    if (addTranscriptionToFirestore(textRes)):
        return ("Transcription added to Firestore.")
    else:
        return ("Error adding transcription to Firestore.")


# # Send audio file to this endpoint using cURL command: `curl -F "audio=@audio_file.wav" http://localhost:5000/transcribe``
# @app.route('/transcribe', methods=['POST'])
# def transcribe():
#     # Transcribe the audio file
#     audio = request.files['audio']
    
#     # Save audio to audio_files directory.
#     audio.save('audio_files/' + audio.filename)
#     whisperResult = whisperModel.transcribe('audio_files/' + audio.filename)
#     textRes = whisperResult['text']
#     if (addTranscriptionToFirestore(textRes)):
#         os.remove('audio_files/' + audio.filename)
#         return ("Transcription added to Firestore.")
#     else:
#         return("Error adding transcription to Firestore.")

# Login route to set user_id in session
@app.route('/login', methods=['POST'])
def login():
    # Get user_id and password from request
    user_id = request.form['user_id']
    password = request.form['password']
    # Check if user_id and password are correct
    user_ref = db.collection(u'users').document(user_id)
    user = user_ref.get()
    if user.exists:
        # Get the data of the document
        user_data = user.to_dict()
        # Hash password for comparison
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if user_data['password'] == hashed_password:
            # Set user_id in session
            session['user_id'] = user_id
            return("Successfully logged in.")
        else:
            return("Error: Incorrect password.")
    else:
        return("Error: User does not exist.")


# Function to hash the password before storing it in the database
def hash_password(password):
    # Use SHA-256 to hash the password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password

# Create account route to add new user to Firestore
@app.route('/signup', methods=['POST'])
def signup():
    # Get the user_id and password from the form data
    user_id = request.form['user_id']
    password = request.form['password']
    # Hash the password before storing it in the database
    hashed_password = hash_password(password)

    # Check if the user_id already exists in the database
    user_ref = db.collection(u'users').document(user_id)
    
    user = user_ref.get()
    if user.exists:
        return("Error: User ID already exists.")
    else:
        # Add the user to the database
        user_ref.set({
            u'user_id': user_id,
            u'password': hashed_password
        })        
        return("Signup successful.")
    

# Logout route to clear user_id from session
@app.route('/logout', methods=['POST'])
def logout():
    # Clear user_id from session
    session.pop('user_id', None)
    return("Successfully logged out.")

if __name__ == '__main__':
    app.run(debug=True)