import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK
cred = credentials.Certificate('faradawn_private_key.json')
firebase_admin.initialize_app(cred)

# Initialize Firestore client
db = firestore.client()

def delete_all_users():
    gardens_ref = db.collection('users')
    query = gardens_ref.stream()
    for doc in query:
        gardens_ref.document(doc.id).delete()
    print("All users deleted successfully")

if __name__ == '__main__':
    delete_all_users()
