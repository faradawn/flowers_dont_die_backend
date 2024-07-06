
from app.firebase import db

def delete_all(collection_name):
    gardens_ref = db.collection(collection_name)
    query = gardens_ref.stream()
    for doc in query:
        gardens_ref.document(doc.id).delete()
    print(f"All {collection_name} deleted successfully")

if __name__ == '__main__':
    delete_all('questions')
