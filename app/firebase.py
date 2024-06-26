import os
import firebase_admin
from firebase_admin import credentials, firestore

# Construct the absolute path to the secret key file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
secret_key_path = os.path.join(BASE_DIR, 'mike-secret-key.json')

cred = credentials.Certificate(secret_key_path)
firebase_admin.initialize_app(cred)
db = firestore.client()