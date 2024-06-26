from app.firebase import db

def fetch_username(uid):
    users_ref = db.collection('users').document(uid)
    user_doc = users_ref.get()
    if user_doc.exists:
        user_data = user_doc.to_dict()
        return user_data.get('username', None)
    return None