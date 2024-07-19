import argparse
from app.firebase import db

def delete_all(collection_name):
    gardens_ref = db.collection(collection_name)
    query = gardens_ref.stream()
    for doc in query:
        gardens_ref.document(doc.id).delete()
    print(f"All documents in the {collection_name} collection deleted successfully")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Delete all documents in a specified Firebase collection.')
    parser.add_argument('--collection', required=True, help='The name of the Firebase collection to delete')
    args = parser.parse_args()

    delete_all(args.collection)
