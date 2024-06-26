from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, RootModel
import firebase_admin
from firebase_admin import credentials, firestore
import uuid
from typing import Dict, List, Optional
import httpx

app = FastAPI()

# Add a route to fetch LeetCode user data
@app.get("/leetcode/{username}")
async def get_leetcode_user(username: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"http://localhost:3000/user/{username}")  # Adjust URL/port as necessary
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail="Failed to fetch LeetCode user data.")
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail="An error occurred while trying to connect to the Node.js service.")


# Initialize Firebase
cred = credentials.Certificate('mike-secret-key.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

def fetch_username(uid):
    users_ref = db.collection('users').document(uid)
    user_doc = users_ref.get()
    if user_doc.exists:
        user_data = user_doc.to_dict()
        return user_data.get('username', None)
    return None

def delete_all_gardens():
    gardens_ref = db.collection('gardens')
    query = gardens_ref.stream()
    for doc in query:
        gardens_ref.document(doc.id).delete()
    print("All gardens deleted successfully")

# Models
class User(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    status: str
    uid: str

class CreateUserResponse(BaseModel):
    status: str
    uid: str

class DeleteAccountResponse(BaseModel):
    status: str

class UIDModel(BaseModel):
    uid: str

@app.post("/create_user", response_model=CreateUserResponse)
async def create_user(user: User):
    delete_all_gardens()  # Remove all old gardens
    users_ref = db.collection('users')
    query = users_ref.where('username', '==', user.username).stream()
    for doc in query:
        return CreateUserResponse(status="already created", uid="none")
    
    uid = f"{user.username}_{uuid.uuid4()}"
    users_ref.document(uid).set({
        'username': user.username,
        'password': user.password
    })
    
    # Create an empty garden for the user
    gardens_ref = db.collection('gardens')
    courses_ref = db.collection('courses')
    
    try:
        # Fetch all courses to create gardens for each
        course_docs = courses_ref.stream()
        for course_doc in course_docs:
            course_data = course_doc.to_dict()
            garden_rows = []
            for i, topic in enumerate(course_data['course_topics'], start=1):
                garden_row = {
                    'row_num': str(i),
                    'topic': topic,
                    'questions_done': []
                }
                garden_rows.append(garden_row)
            
            garden_data = {
                'uid': uid,
                'username': user.username,
                'course_id': course_doc.id,
                'garden_rows': garden_rows
            }
            gardens_ref.add(garden_data)
    except Exception as e:
        return HTTPException(status_code=500, detail=f"Error setting up gardens: {str(e)}")

@app.post("/login", response_model=LoginResponse)
async def login(userlog: UserLogin):
    users_ref = db.collection('users')
    query = users_ref.where('username', '==', userlog.username).stream()
    for doc in query:
        user_data = doc.to_dict()
        if user_data['password'] == userlog.password:
            return LoginResponse(status="success", uid=doc.id)
        else:
            return LoginResponse(status="failed", uid="none")
    
    return LoginResponse(status="failed", message="Please create an account first", uid="none")

@app.post("/delete_account", response_model=DeleteAccountResponse)
async def delete_account(uid_model: UIDModel):
    uid = uid_model.uid
    users_ref = db.collection('users')
    gardens_ref = db.collection('gardens')

    try:
        # Delete the user
        user_doc = users_ref.document(uid).get()
        if user_doc.exists:
            users_ref.document(uid).delete()
        else:
            raise HTTPException(status_code=404, detail="User not found")

        # Delete the user's gardens
        garden_query = gardens_ref.where('uid', '==', uid).stream()
        for doc in garden_query:
            gardens_ref.document(doc.id).delete()

        return DeleteAccountResponse(
            status="success",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# === Garden section 
def calculate_sunlight(garden_rows):
    sunlight = 0
    for row in garden_rows:
        sunlight += row['conditions']['easy'] * 50
        sunlight += row['conditions']['medium'] * 100
        sunlight += row['conditions']['hard'] * 200
    return sunlight


class GardenLoadRequest(BaseModel):
    uid: str
    course_id: str

class GardenRow(BaseModel):
    row_num: int
    topic: str
    questions_done: List[str]

class GardenLoadResponse(BaseModel):
    status: str
    message: str
    course_id: str
    course_name: str
    garden_rows: List[GardenRow]



# If no such garden, create a new one based on the course_topic (fetch from "courses" collection).
# Else, fetch the garden and calcuate the total sunlight:
# In conditions, easy: 1 means that there is 1 easy questions. 
# Each easy flower worth 50 sunlight, a medium worth 100, a hard worth 200.
@app.post("/garden/load_garden", response_model=GardenLoadResponse)
async def garden_page_load(request: GardenLoadRequest):
    gardens_ref = db.collection('gardens')
    garden_query = gardens_ref.where('uid', '==', request.uid).where('course_id', '==', request.course_id).stream()

    garden_data = None
    for doc in garden_query:
        garden_data = doc.to_dict()
        garden_doc_id = doc.id
        break

    if garden_data:
        sunlight = calculate_sunlight(garden_data['garden_rows'])
        garden_data['sunlight'] = sunlight
        
        # Update the sunlight in Firestore
        gardens_ref.document(garden_doc_id).update({'sunlight': sunlight})
        
        return GardenLoadResponse(
            status="success",
            message="Garden loaded successfully",
            course_id=garden_data['course_id'],
            sunlight=sunlight,
            garden_rows=garden_data['garden_rows']
        )
    else:
        courses_ref = db.collection('courses').document(request.course_id)
        course_doc = courses_ref.get()
        if not course_doc.exists:
            raise HTTPException(status_code=404, detail="Course not found")

        course_data = course_doc.to_dict()
        garden_rows = []
        for i, topic in enumerate(course_data['course_topics'], start=1):
            garden_row = {
                'row_num': str(i),
                'topic': topic,
                'conditions': {'easy': 0, 'medium': 0, 'hard': 0},
                'questions': {'q1_id': 'none', 'q2_id': 'none', 'q3_id': 'none'}
            }
            garden_rows.append(garden_row)
        
        garden_data = {
            'uid': request.uid,
            'username': fetch_username(request.uid),
            'course_id': request.course_id,
            'sunlight': 0,
            'garden_rows': garden_rows
        }
        
        gardens_ref.add(garden_data)

        return GardenLoadResponse(
            status="success",
            message="New garden created successfully",
            course_id=garden_data['course_id'],
            sunlight=0,
            garden_rows=garden_rows
        )


class GetQuestionRequest(BaseModel):
    uid: str
    course_id: str
    topic: str

class GetQuestionResponse(BaseModel):
    status: str
    message: str
    question_id: str    
    difficulty: str
    topic: str
    answer: str
    question: str
    question_number: str
    options: List[str]
    time_limit: int

# if question_id is provided, directly use the question_id
# else, go to questions to find a question with matching {course_id, topic, difficulty}. Just return the first one.
@app.post("/garden/get_question", response_model=GetQuestionResponse)
async def get_question(request: GetQuestionRequest):
    questions_ref = db.collection('questions')

    # Find a question with matching {course_id, topic}
    question_query = questions_ref.where('course_id', '==', request.course_id)\
                                  .where('topic', '==', request.topic)\
                                  .limit(1).stream()
    question_data = None
    for doc in question_query:
        if doc.exists:
            question_data = doc.to_dict()
            question_data['question_id'] = doc.id
            break
    
    if not question_data:
        raise HTTPException(status_code=404, detail="No matching question found")
    
    return GetQuestionResponse(
        status="success",
        message="Question retrieved successfully",
        question_id=question_data['question_id'],
        difficulty=question_data['difficulty'],
        topic=question_data['topic'],
        answer=question_data['answer'],
        question=question_data['question'],
        question_number=question_data['question_number'],
        options=question_data['options'],
        time_limit=question_data['time_limit']
    )


class SubmitAnswerRequest(BaseModel):
    uid: str
    neighbor_uid: str
    course_id: str
    question_id: str
    response_time: int
    user_answer: str
    correct_answer: str


class SubmitAnswerResponse(BaseModel):
    status: str


def update_flower_count(garden_rows, topic, difficulty, increment):
    for row in garden_rows:
        if row['topic'] == topic:
            row['conditions'][difficulty] += increment
            return

# If answer is correct, add 1 flower to the my garden at the location {topic, difficulty}
# Also deduct 1 flower at the neighbor's garden's position
# If answer incorrect, do nothing. 
# If neighbor's username is OG, don't deduct 
@app.post("/garden/submit_answer", response_model=SubmitAnswerResponse)
async def submit_answer(request: SubmitAnswerRequest):
    gardens_ref = db.collection('gardens')
    
    # Check if the answer is correct
    if request.user_answer == request.correct_answer:
        try:
            # Fetch the user's garden
            user_garden_query = gardens_ref.where('uid', '==', request.uid).where('course_id', '==', request.course_id).stream()
            user_garden_data = None
            user_garden_doc_id = None

            for doc in user_garden_query:
                user_garden_data = doc.to_dict()
                user_garden_doc_id = doc.id
                break

            if not user_garden_data:
                raise HTTPException(status_code=404, detail="User's garden not found")

            # Fetch the neighbor's garden
            neighbor_garden_query = gardens_ref.where('uid', '==', request.neighbor_uid).where('course_id', '==', request.course_id).stream()
            neighbor_garden_data = None
            neighbor_garden_doc_id = None

            for doc in neighbor_garden_query:
                neighbor_garden_data = doc.to_dict()
                neighbor_garden_doc_id = doc.id
                break

            if not neighbor_garden_data:
                raise HTTPException(status_code=404, detail="Neighbor's garden not found")

            # Add 1 flower to the user's garden
            update_flower_count(user_garden_data['garden_rows'], request.topic, request.difficulty, 1)

            # Deduct 1 flower from the neighbor's garden
            if neighbor_garden_data['username'] != 'OG':
                update_flower_count(neighbor_garden_data['garden_rows'], request.topic, request.difficulty, -1)

            # Update the gardens in Firestore
            gardens_ref.document(user_garden_doc_id).set(user_garden_data)
            gardens_ref.document(neighbor_garden_doc_id).set(neighbor_garden_data)

            return SubmitAnswerResponse(
                status="success",
                message="Answer is correct. Garden updated successfully."
            )
        except Exception as e:
            return SubmitAnswerResponse(
                status="error",
                message=f"An error occurred: {str(e)}"
            )
    else:
        return SubmitAnswerResponse(
            status="success",
            message="Answer is incorrect. No changes made."
        )



# === Courses Section 


class CoursesRequest(BaseModel):
    uid: str

class CoursesItem(BaseModel):
    course_id: str
    course_name: str

class CoursesResponse(RootModel[List[CoursesItem]]):
    pass

@app.post("/courses", response_model=CoursesResponse)
async def courses_page(request: CoursesRequest):
    courses_ref = db.collection('courses')
    query = courses_ref.stream()
    res_arr = []
    for doc in query:
        course_data = doc.to_dict()
        res_arr.append(CoursesItem(course_id=doc.id, course_name=course_data['course_name']))
    return CoursesResponse(root=res_arr)

# Select Neighbor
class SelectNeighborRequest(BaseModel):
    uid: str        
    course_id: str  

class SelectNeighborItem(BaseModel):
    uid: str
    username: str
    total_flowers: int

class SelectNeighborResponse(RootModel[List[SelectNeighborItem]]):
    pass

# Read from "gardens" collection and fetch all gardens 
# with matching course_id AND non-matching uid (exclude myself)
@app.post("/select_neighbor", response_model=SelectNeighborResponse)
async def select_neighbor(request: SelectNeighborRequest):
    gardens_ref = db.collection('gardens')
    
    # Query gardens with matching course_id
    garden_query = gardens_ref.where('course_id', '==', request.course_id).stream()
    neighbor_list = []

    for doc in garden_query:
        garden_data = doc.to_dict()
        if garden_data['uid'] != request.uid:
            # Calculate sunlight just to be safe
            sunlight = calculate_sunlight(garden_data['garden_rows'])
            if sunlight != garden_data['sunlight']:
                # Update the sunlight in Firestore
                gardens_ref.document(doc.id).update({'sunlight': sunlight})
            neighbor_list.append(SelectNeighborItem(
                uid=garden_data['uid'],
                username=garden_data['username'],
                sunlight=sunlight
            ))

    return SelectNeighborResponse(root=neighbor_list)




# /get_garden 
# user post {uid, course_id}
# return {course_id, garden_rows: [{row_num=int, topic=str, questions=list(str)}]}
# Define the request model

@app.post("/get_garden", response_model=GardenLoadResponse)
async def get_garden(request: GardenLoadRequest):
    delete_all_gardens()  # Remove all old gardens
    
    gardens_ref = db.collection('gardens')
    courses_ref = db.collection('courses')

    garden_query = gardens_ref.where('uid', '==', request.uid).where('course_id', '==', request.course_id).stream()
    garden_data = None
    for doc in garden_query:
        if doc.exists:
            garden_data = doc.to_dict()
            break

    if garden_data:
        return GardenLoadResponse(
            status="success",
            message="Garden retrieved successfully",
            course_id=garden_data['course_id'],
            course_name=garden_data.get('course_name', ''),
            garden_rows=garden_data['garden_rows']
        )
    else:
        course_doc = courses_ref.document(request.course_id).get()
        if not course_doc.exists:
            raise HTTPException(status_code=404, detail="Course not found")

        course_data = course_doc.to_dict()
        course_name = course_data.get('course_name', '')

        # Create a new garden based on course topics
        garden_rows = []
        for i, topic in enumerate(course_data.get('course_topics', []), start=1):
            garden_row = GardenRow(
                row_num=i,
                topic=topic,
                questions_done=[]
            )
            garden_rows.append(garden_row)
        
        garden_data = {
            'uid': request.uid,
            'username': fetch_username(request.uid),
            'course_id': request.course_id,
            'garden_rows': garden_rows
        }
        
        gardens_ref.add(garden_data)

        return GardenLoadResponse(
            status="success",
            message="New garden created successfully",
            course_id=request.course_id,
            course_name=course_name,
            garden_rows=garden_rows
        )