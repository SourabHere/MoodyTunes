from fastapi import APIRouter
from utils.gemini_utils import hello_model


router = APIRouter()

@router.get("/hello_response")
def hello_response():
    return hello_model()  


