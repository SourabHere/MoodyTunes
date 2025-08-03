import json
import re
from typing import Dict, List
from services.LLM_interface import LLMInterface
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()


class GeminiService(LLMInterface):

    def __init__(self):
        self.name = "gemini"
        self.token = os.getenv("GEMINI_API_KEY")
        self.model = genai.GenerativeModel("models/gemini-2.0-flash-lite")

        if not self.token:
            raise EnvironmentError("GEMINI_API_KEY not found in environment variables.")
        
        
        genai.configure(api_key=self.token)

        

    def hello_world(self):
        try:
            response = self.model.generate_content("hi")
            return response.text.strip()
        except Exception as e:
            return str({"error": str(e)})
        
        
    def classify_songs_by_mood(self, playlist_name: str, mood: str, songs: List[Dict[str, str]]) -> str:
    
        prompt = f'''
        I have the following list of songs from a Spotify playlist named "{playlist_name}".

        The user wants a playlist with a "{mood}" mood.

        Here is the list of songs:
        {songs}

        Please return a filtered list of songs that match the mood "{mood}" in this format only:
        [
        {{"artist": "...", "track": "...", "spotify_id": "...", "mood_match": true}}
        ]

        Respond with only JSON. Avoid extra comments.
        '''

        try:
            
            response = self.model.generate_content(prompt)

            output = response.text.strip()

            if output.startswith("```json"):
                output = output.replace("```json", "").replace("```", "").strip()

            return json.loads(output)

            # return self.format_gemini_response(response.text.strip())
        except Exception as e:
            return str({"error": str(e)})
        
    
    def generate_song_descriptions(self, song_name: str, artist_name: str) -> str:
        prompt = f'''
        Generate a detailed description for the song "{song_name}" by "{artist_name}".
        The description should include the song's themes, style, mood and any notable elements.
        Respond with only the description text briefly in 80-100 words.
        '''

        try:
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return str({"error": str(e)})
        

    def classify_song_ids_by_mood(self, playlist_name: str, mood: str, songs: List[Dict[str, str]]) -> List[Dict[str, str]]:

        prompt = f'''
            You are a music assistant.

            The user wants to create a playlist named "{playlist_name}" with a "{mood}" mood.

            Here is the list of songs:
            {songs}

            Please return a JSON list ONLY in the following format:
            [
            {{"spotify_id": "<id>", "mood_match": true/false}},
            ...
            ]

            Only return valid JSON. No markdown, no explanations, no extra text.
            '''

        try:
            
            response = self.model.generate_content(prompt)
            output = response.text.strip()


            if output.startswith("```json"):
                output = output.replace("```json", "").replace("```", "").strip()

            return json.loads(output)

        except Exception as e:
            return [{"error": str(e)}]


