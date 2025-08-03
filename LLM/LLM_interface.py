from abc import ABC, abstractmethod
from typing import Dict, List

class LLMInterface(ABC):
    @abstractmethod
    def classify_songs_by_mood(self, playlist_name: str, mood: str, songs: List[Dict[str, str]]) -> list:
        """
        Classify songs by mood using the LLM.
        
        :param song_ids: List of song IDs to classify.
        :param mood: The mood to classify the songs into.
        :return: List of classified song IDs.
        """
        pass

    @abstractmethod
    def generate_song_descriptions(self, song_name: str, artist_name:str) -> str:
        """
        Generate descriptions for a song using the LLM.
        
        :param song_id: song ID to generate descriptions for.
        :param artist_name: Name of the artist for the song.
        :return: Description of the song.
        """
        pass

    @abstractmethod
    def classify_song_ids_by_mood(self, playlist_name: str, mood: str, songs: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Classify song IDs by mood using the LLM.
        
        :param playlist_name: Name of the playlist.
        :param mood: The mood to classify the songs into.
        :param songs: List of song dicts, each containing 'spotify_id'.
        :return: List of dictionaries with 'spotify_id' and 'mood_match'.
        """
        pass

    @abstractmethod
    def hello_world(self) -> str:
        """
        A simple method to test the connection with the LLM.
        
        :return: A greeting message.
        """
        pass