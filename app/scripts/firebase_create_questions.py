from app.firebase import db
import requests

def get_course_id():
    course_id = None
    for course in db.collection('courses').stream():
        course_id = course.id
        break
    return course_id

def fetch_leetcode_date(slug):
    base_url = "https://alfa-leetcode-api.onrender.com/select"
    params = {"titleSlug": slug}

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        return data
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None

def upload_questions(course_id='Software_Engineering_1', file_name='app/scripts/claude_question_list.csv'):
    import csv
    import os

    firebase_ref = db.collection('questions')
    questions_data = []

    with open(file_name, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            question_dict = {
                'course_id': course_id,
                'topic': row['topic'],
                'difficulty': row['difficulty'],
                'slug': row['slug'],
                'answer': 'A',  # Assuming the correct solution is always 'A'
                'question': row['question'],
                'question_number': row['question_number'],
                'options': [
                    row['correct_approach'],
                    row['incorrect_approach_1'],
                    row.get('incorrect_approach_2', ''),
                ],
                'time_limit': 90
            }
            
            # Create the document ID as (topic|difficulty|slug)
            doc_id = f"{row['topic']}|{row['difficulty']}|{row['slug']}"
            
            # Use the created document ID when adding the question to Firestore
            firebase_ref.document(doc_id).set(question_dict)
            
            print(f"Adding question_number: {question_dict['question_number']}, topic: {question_dict['topic']}, difficulty: {question_dict['difficulty']}")

if __name__ == '__main__':
    course_id = get_course_id()
    print("Got course_id", course_id)
    upload_questions(course_id=course_id, file_name='app/scripts/claude_question_list.csv')

# Usage
# python3 -m app.scripts.firebase_delete_collection --collection questions
# python3 -m app.scripts.firebase_create_questions
