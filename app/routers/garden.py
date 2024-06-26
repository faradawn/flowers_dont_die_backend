from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.firebase import db
from app.utils import fetch_username

router = APIRouter()

# Models
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

@router.post("/get_garden", response_model=GardenLoadResponse)
async def get_garden(request: GardenLoadRequest):
    try:
        # Query the gardens collection
        gardens_ref = db.collection('gardens')
        query = gardens_ref.where('uid', '==', request.uid).where('course_id', '==', request.course_id).limit(1).get()

        if not query:
            return GardenLoadResponse(
                status="failed",
                message="Garden not found",
                course_id="",
                course_name="",
                garden_rows=[]
            )

        garden_doc = query[0]
        garden_data = garden_doc.to_dict()

        # Fetch course name
        courses_ref = db.collection('courses')
        course_doc = courses_ref.document(request.course_id).get()
        
        if not course_doc.exists:
            return GardenLoadResponse(
                status="failed",
                message="Course not found",
                course_id=request.course_id,
                course_name="",
                garden_rows=[]
            )

        course_data = course_doc.to_dict()
        course_name = course_data.get('course_name', '')

        # Prepare garden rows
        garden_rows = [
            GardenRow(
                row_num=int(row['row_num']),
                topic=row['topic'],
                questions_done=row['questions_done']
            )
            for row in garden_data.get('garden_rows', [])
        ]

        return GardenLoadResponse(
            status="success",
            message="Garden loaded successfully",
            course_id=request.course_id,
            course_name=course_name,
            garden_rows=garden_rows
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")