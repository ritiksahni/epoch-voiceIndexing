import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Use the application default credentials
cred = firebase_admin.credentials.Certificate('.speechnotes-ServiceKey.json')
firebase_admin.initialize_app(cred)

db = firestore.client()
