# Create an official guide user.
'''

# First, fetch the uid with useranme OG. 

# Second, delete all items in the "courses" collection in firebase and create a new course with COURSE_NAME. 
# Let the new course's doc_id be COURSE_NAME concatenate (with underscore) with uuid().
# Let the new course's schema be {course_name: COURSE_NAME, course_topics: COURSE_TOPICS array}

# Third, insert the questions below (questions_data) into the "questions" collection.
# Keep the Topic, difficulty, and question_id for each questions you created. Store in a map with key (topic, difficulty) and value (question_id).

# Fourth, in the gardens collection, create a garden corresponding to OG's uid and course_id such as the below 
# (but don't hard code, use loop using the COURSE_TOPICS). 
# Set the q1_id, q2_id, etc with the questions you created (use the map)
garden_rows = [
        GardenRow(row_num="1", topic="Array", conditions=Condition(easy=0, medium=0, hard=0), questions=Questions(q1_id="none", q2_id="none", q3_id="none")),
        GardenRow(row_num="2", topic="Linked List", conditions=Condition(easy=0, medium=0, hard=0), questions=Questions(q1_id="none", q2_id="none", q3_id="none")),
        GardenRow(row_num="3", topic="Stack", conditions=Condition(easy=0, medium=0, hard=0), questions=Questions(q1_id="none", q2_id="none", q3_id="none")),
        GardenRow(row_num="4", topic="Queue", conditions=Condition(easy=0, medium=0, hard=0), questions=Questions(q1_id="none", q2_id="none", q3_id="none")),
        GardenRow(row_num="5", topic="Binary Tree", conditions=Condition(easy=0, medium=0, hard=0), questions=Questions(q1_id="none", q2_id="none", q3_id="none")),
        GardenRow(row_num="6", topic="Hash Table", conditions=Condition(easy=0, medium=0, hard=0), questions=Questions(q1_id="none", q2_id="none", q3_id="none")),
        GardenRow(row_num="7", topic="Graph", conditions=Condition(easy=0, medium=0, hard=0), questions=Questions(q1_id="none", q2_id="none", q3_id="none")),
        GardenRow(row_num="8", topic="Heap", conditions=Condition(easy=0, medium=0, hard=0), questions=Questions(q1_id="none", q2_id="none", q3_id="none")),
        GardenRow(row_num="9", topic="Sorting", conditions=Condition(easy=0, medium=0, hard=0), questions=Questions(q1_id="none", q2_id="none", q3_id="none")),
        GardenRow(row_num="10", topic="Dynamic Programming", conditions=Condition(easy=0, medium=0, hard=0), questions=Questions(q1_id="none", q2_id="none", q3_id="none"))
    ]

# Insert the garden item into firebase with the schema {uid, course_id, sunlight, garden_rows}

'''
import firebase_admin
from firebase_admin import credentials, firestore
import uuid
from question_data import questions_data

# Initialize Firebase Admin SDK
cred = credentials.Certificate('faradawn_private_key.json')
firebase_admin.initialize_app(cred)

# Initialize Firestore client
db = firestore.client()

USERNAME = 'OG'
COURSE_NAME = 'Software_Engineer'
COURSE_TOPICS = ["Array", "Linked List", "Stack", "Queue", "Binary Tree", "Hash Table", "Graph", "Heap", "Sorting", "Dynamic Programming"]

def fetch_uid(username):
    users_ref = db.collection('users')
    query = users_ref.where('username', '==', username).stream()
    for doc in query:
        return doc.id
    return None

def delete_all_courses():
    courses_ref = db.collection('courses')
    query = courses_ref.stream()
    for doc in query:
        courses_ref.document(doc.id).delete()
    print("Deleted all courses")

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

def create_new_course(course_name, course_topics):
    course_id = f"{course_name}_{uuid.uuid4()}"
    course_data = {
        'course_name': course_name,
        'course_topics': course_topics
    }
    db.collection('courses').document(course_id).set(course_data)
    return course_id


def add_questions(questions_data, course_id):
    questions_ref = db.collection('questions')
    question_ids = {}
    for question_data in questions_data:
        question_data['course_id'] = course_id
        doc_ref = questions_ref.add(question_data)[1]
        topic = question_data['topic']
        difficulty = question_data['difficulty']
        if (topic, difficulty) not in question_ids:
            question_ids[(topic, difficulty)] = []
        question_ids[(topic, difficulty)].append(doc_ref.id)
    return question_ids

def create_garden(uid, course_id, course_topics, question_ids):
    # delete previous garden
    garden_ref = db.collection('garden')
    query = garden_ref.where('course_id', '==', course_id).where('uid', '==', uid).stream()
    for doc in query:
        garden_ref.document(doc.id).delete()
        print("Deleting previous garden")
    


    # create new 
    garden_rows = []
    for i, topic in enumerate(course_topics, start=1):
        q1_id = question_ids.get((topic, 'easy'), ['none'])[0]
        q2_id = question_ids.get((topic, 'medium'), ['none'])[0]
        q3_id = question_ids.get((topic, 'hard'), ['none'])[0]
        
        conditions = {'easy': 0, 'medium': 0, 'hard': 0}
        
        if q1_id != 'none':
            conditions['easy'] = 1
        if q2_id != 'none':
            conditions['medium'] = 1
        if q3_id != 'none':
            conditions['hard'] = 1
        
        garden_row = {
            'row_num': str(i),
            'topic': topic,
            'conditions': conditions,
            'questions': {
                'q1_id': q1_id,
                'q2_id': q2_id,
                'q3_id': q3_id
            }
        }
        garden_rows.append(garden_row)
    
    garden_data = {
        'uid': uid,
        'username': USERNAME,
        'course_id': course_id,
        'sunlight': 0,
        'garden_rows': garden_rows
    }
    
    db.collection('gardens').add(garden_data)


uid = fetch_uid(USERNAME)
if uid:
    delete_all_courses()
    delete_all_gardens()
    delete_all_questions()

    course_id = create_new_course(COURSE_NAME, COURSE_TOPICS)
    question_ids = add_questions(questions_data, course_id)
    create_garden(uid, course_id, COURSE_TOPICS, question_ids)
    print("Done! Created questions", question_ids)
else:
    print(f"User with username {USERNAME} not found.")
