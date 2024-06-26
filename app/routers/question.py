from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.firebase import db

router = APIRouter()

# Models
class GetQuestionRequest(BaseModel):
    uid: str
    course_id: str
    topic: str
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

@router.post("/submit_answer", response_model=SubmitAnswerResponse)
async def submit_answer(request: SubmitAnswerRequest):
    gardens_ref = db.collection('gardens')
    if request.user_answer == request.correct_answer:
        try:
            user_garden_query = gardens_ref.where('uid', '==', request.uid).where('course_id', '==', request.course_id).stream()
            user_garden_data = None
            user_garden_doc_id = None
            for doc in user_garden_query:
                user_garden_data = doc.to_dict()
                user_garden_doc_id = doc.id
                break

            if not user_garden_data:
                raise HTTPException(status_code=404, detail="User's garden not found")

            neighbor_garden_query = gardens_ref.where('uid', '==', request.neighbor_uid).where('course_id', '==', request.course_id).stream()
            neighbor_garden_data = None
            neighbor_garden_doc_id = None
            for doc in neighbor_garden_query:
                neighbor_garden_data = doc.to_dict()
                neighbor_garden_doc_id = doc.id
                break

            if not neighbor_garden_data:
                raise HTTPException(status_code=404, detail="Neighbor's garden not found")

        
            gardens_ref.document(user_garden_doc_id).set(user_garden_data)
            gardens_ref.document(neighbor_garden_doc_id).set(neighbor_garden_data)

            return SubmitAnswerResponse(status="success")
        except Exception as e:
            return SubmitAnswerResponse(status="error", message=f"An error occurred: {str(e)}")
    else:
        return SubmitAnswerResponse(status="success", message="Answer is incorrect. No changes made.")
