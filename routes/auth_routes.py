from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

from auth.spotify_auth import get_spotify_oauth

router = APIRouter()


@router.get("/login")
def login():
    sp_oauth = get_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    
    return {
        "auth_url": auth_url,
        "description": "Please visit the URL to authorize the application."
    }

@router.get("/callback")
def callback(request: Request):
    code = request.query_params.get("code")
    sp_oauth = get_spotify_oauth()
    token_info = sp_oauth.get_access_token(code)


    with open("token.txt", "w") as f:
        f.write(token_info["access_token"])

    return RedirectResponse(url="/docs")
