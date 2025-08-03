from fastapi import FastAPI
from routes import auth_routes, spotify_routes, prompt_app_routes

app = FastAPI(
    title="Smart Spotify Playlist Generator",
    description="Generates mood-based playlists"
)


@app.get("/")
def root():
    return {"message": "Spotify Mood Playlist Creator API"}


app.include_router(auth_routes.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(spotify_routes.router, prefix="/api/v1/spotify", tags=["Playlist"])
app.include_router(prompt_app_routes.router, prefix="/api/v1/gemini", tags=["LLM"])



