import os
import json
from dotenv import load_dotenv

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


load_dotenv('./.env')


# Use the application default credentials
serviceAccount = os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY');
serviceAccountCredentials = json.loads(serviceAccount)

cred = firebase_admin.credentials.Certificate(serviceAccountCredentials)
firebase_admin.initialize_app(cred)

db = firestore.client()
