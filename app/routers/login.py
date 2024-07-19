from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.firebase import db
import uuid

router = APIRouter()

# Models
class User(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class ResponseModel(BaseModel):
    status: str
    message: str
    uid: str = ""

class UID(BaseModel):
    uid: str

@router.post("/create_user", response_model=ResponseModel)
async def create_user(user: User):
    users_ref = db.collection('users')
    gardens_ref = db.collection('gardens')

    if users_ref.where('username', '==', user.username).get():
        return ResponseModel(status="failed", message="User already exists")

    uid = f"{user.username}_{uuid.uuid4()}"
    users_ref.document(uid).set(user.dict())


    return ResponseModel(status="success", message="User created successfully", uid=uid)

@router.post("/login", response_model=ResponseModel)
async def login(userlog: UserLogin):
    query = db.collection('users').where('username', '==', userlog.username).limit(1).get()
    if query and query[0].to_dict()['password'] == userlog.password:
        return ResponseModel(status="success", message="Login successful", uid=query[0].id)
    return ResponseModel(status="failed", message="Invalid username or password")

@router.post("/delete_account", response_model=ResponseModel)
async def delete_account(uid_request: UID):
    uid = uid_request.uid
    try:
        users_ref = db.collection('users')
        gardens_ref = db.collection('gardens')

        user_doc = users_ref.document(uid).get()
        if not user_doc.exists:
            return ResponseModel(status="failed", message="User not found")

        users_ref.document(uid).delete()
        for doc in gardens_ref.where('uid', '==', uid).stream():
            doc.reference.delete()

        return ResponseModel(status="success", message="Account deleted successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")