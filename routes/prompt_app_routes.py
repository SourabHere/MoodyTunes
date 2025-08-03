from fastapi import APIRouter
from services.prompt_app_service import PromptAppService


router = APIRouter()

@router.get("/hello_response")
def hello_response():
    return PromptAppService().hello_world()  


