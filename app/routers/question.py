from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.firebase import db
import random

router = APIRouter()

# Models
class GetQuestionRequest(BaseModel):
    uid: str
    course_id: str
    topic: Optional[str] = None
    difficulty: Optional[str] = None

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

@router.post("/get_question", response_model=GetQuestionResponse)
async def get_question(request: GetQuestionRequest):
    questions_ref = db.collection('questions')

    if request.topic is None or request.topic == '':
        # If topic is None, get all questions for the course
        all_questions_query = questions_ref.where('course_id', '==', request.course_id).stream()
        all_questions = [doc for doc in all_questions_query if doc.exists]
        
        if all_questions:
            # Select a random question among all questions
            question_doc = random.choice(all_questions)
            question_data = question_doc.to_dict()
            question_data['question_id'] = question_doc.id
        else:
            # If no questions found for the course, return an error
            return GetQuestionResponse(
                status="failed",
                message="No questions found for this course",
                question_id="No Question",
                difficulty="Easy",
                topic="No question",
                answer="A",
                question="Sorry, more questions on their way!",
                question_number='Leetcode 0.',
                options=['Sorry', 'Sorry', 'Sorry'],
                time_limit=60
            )
    else:
        # If topic is provided, proceed with the original logic
        question_query = questions_ref.where('course_id', '==', request.course_id)\
            .where('topic', '==', request.topic)\
            .stream()
        matching_questions = [doc for doc in question_query if doc.exists]
        
        if matching_questions:
            question_doc = random.choice(matching_questions)
            question_data = question_doc.to_dict()
            question_data['question_id'] = question_doc.id
        else:
            return GetQuestionResponse(
                status="failed",
                message="No questions found for this topic",
                question_id="More questions on this topic is on its way!",
                difficulty="Easy",
                topic="No question",
                answer="Z",
                question="Sorry, more questions of this kind are on their way!",
                question_number='Leetcode 0.',
                options=['Sorry', 'Sorry', 'Sorry'],
                time_limit=60
            )

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
    course_id: str
    topic: Optional[str] = None
    question_id: str
    response_time: int
    user_answer: str
    correct_answer: str

class SubmitAnswerResponse(BaseModel):
    status: str
    message: str


'''
Firebase garden [
  garden_id {
    uid: str,
    username: str,
    course_id: str,
    garden_rows: List[
      {
        row_num: int,
        topic: str,
        questions_done: List[str]
      }
    ]
  }
]

'''

# If the answer is correct, add the question id to the user's garden's question_done
# Note that you should find row with the corresponding topic
@router.post("/submit_answer", response_model=SubmitAnswerResponse)
async def submit_answer(request: SubmitAnswerRequest):
    gardens_ref = db.collection('gardens')
    questions_ref = db.collection('questions')

    # Check if the answer is correct
    if request.user_answer == request.correct_answer:
        # First, fetch the question to get its topic
        question_doc = questions_ref.document(request.question_id).get()
        if not question_doc.exists:
            return SubmitAnswerResponse(
                status="failed",
                message="Question not found"
            )
        
        question_data = question_doc.to_dict()
        question_topic = question_data.get('topic')

        if not question_topic:
            return SubmitAnswerResponse(
                status="failed",
                message="Question topic not found"
            )

        # Query for the user's garden
        garden_query = gardens_ref.where('uid', '==', request.uid).where('course_id', '==', request.course_id).limit(1).get()

        if not garden_query:
            return SubmitAnswerResponse(
                status="failed",
                message="User garden not found"
            )

        garden_doc = garden_query[0]
        garden_data = garden_doc.to_dict()

        # Find the correct row for the topic
        target_row = None
        for row in garden_data.get('garden_rows', []):
            if row['topic'] == question_topic:
                target_row = row
                # if request.question_id not in target_row['questions_done']:
                target_row['questions_done'].append(request.question_id)
                gardens_ref.document(garden_doc.id).set(garden_data)
                break

        if target_row is not None:
            return SubmitAnswerResponse(
                status="success",
                message=f"Correct. Updated garden row with topic {question_topic}"
            )
        else:
            return SubmitAnswerResponse(
                status="success",
                message=f"Correct. But didn't find the target row for question_topic {question_topic}"
            )

    else:
        return SubmitAnswerResponse(
            status="success",
            message=f"Incorrect. User answer: {request.user_answer}, correct answer: {request.correct_answer}"
        )

class QRequest(BaseModel):
    question_slug: str
class QRes(BaseModel):
    res: str

@router.post("/get_top_vote", response_model=QRes)
async def submit_answer(request: QRequest):
    return QRes(res="Answer 1: The main idea is the same with problem Linked List Cycle II,https://leetcode.com/problems/linked-list-cycle-ii/. Use two pointers the fast and the slow. The fast one goes forward two steps each time, while the slow one goes only step each time. They must meet the same item when slow==fast. In fact, they meet in a circle, the duplicate number must be the entry point of the circle when visiting the array from nums[0]. Next we just need to find the entry point. We use a point(we can use the fast one before) to visit form begining with one step each time, do the same job to slow. When fast==slow, they meet at the entry point of the circle. The easy understood code is as follows. ")