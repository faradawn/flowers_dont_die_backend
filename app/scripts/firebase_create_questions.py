from app.firebase import db
def get_course_id():
    course_id = None
    for course in db.collection('courses').stream():
        course_id = course.id
        break
    return course_id


def delete_all_questions(course_id=None):
  questions_ref = db.collection('questions')

  if course_id is None:
      print("Deleting all questions")
      query = questions_ref.stream()
  else:
      print(f"Deleting questions with course id: {course_id}")
      query = questions_ref.where('course_id', '==', course_id).stream()

  for doc in query:
      questions_ref.document(doc.id).delete()
        
def delete_all_gardens():
    gardens_ref = db.collection('gardens')
    query = gardens_ref.stream()
    for doc in query:
        gardens_ref.document(doc.id).delete()
    print("Deleted all gardens")


def get_questions():
    import csv
    import os
    # Get the directory where the current script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Hard code the file name
    
    # Construct the absolute path to the CSV file
    # absolute_path = os.path.join(script_dir, file_name)
    
    file_name = 'app/scripts/claude_question_list.csv'
    questions_data = []
    
    with open(file_name, mode='r') as file:
        csv_reader = csv.DictReader(file)
        
        for row in csv_reader:
            question_dict = {
                'course_id': 'Software_Engineer_53fc0699-7eb2-4e66-bdd9-e1fa51aa4c3c',
                'topic': row['topic'],
                'difficulty': row['difficulty'],
                'answer': 'A',  # Assuming the correct solution is always 'A'
                'question': row['question'],
                'question_number': 'Leetcode ' + row['question_number'],
                'options': [
                    row['correct_approach'],
                    row['incorrect_approach_1'],
                    row.get('incorrect_approach_2', ''),
                ],
                'time_limit': 60
            }
            questions_data.append(question_dict)
    
    return questions_data


def add_questions(course_id):
    questions_ref = db.collection('questions')
    question_array = get_questions()
    for question_data in question_array:
        print(f"Adding question_number: {question_data['question_number']}, topic: {question_data['topic']}, difficulty: {question_data['difficulty']}")
        question_data['course_id'] = course_id
        doc_ref = questions_ref.add(question_data)[1]
    print(f"Added {len(question_array)} questions")


if __name__ == '__main__':
    course_id = get_course_id()
    print("Got course_id", course_id)
    add_questions(course_id)