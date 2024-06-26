
from app.firebase import db

def delete_all_users():
    gardens_ref = db.collection('users')
    query = gardens_ref.stream()
    for doc in query:
        gardens_ref.document(doc.id).delete()
    print("All users deleted successfully")

def delete_all_gardens():
    gardens_ref = db.collection('gardens')
    query = gardens_ref.stream()
    for doc in query:
        gardens_ref.document(doc.id).delete()
    print("All gardens deleted successfully")


if __name__ == '__main__':
    delete_all_users()
    delete_all_gardens()
