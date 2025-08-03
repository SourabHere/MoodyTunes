# 🎧 MoodyTunes

**MoodyTunes** is an LLM-powered playlist mood filter.  

Built for people (like me) who have one massive Spotify playlist with every kind of vibe in it — from sad boy monsoon beats to party bangers — and don’t want to spend 3+ hours sorting them manually.

So instead of doing the boring task of creating separate playlists... I wrote an app. Because obviously, coding a full app is way easier than manually dragging songs. 🤷‍♂️

After all, what's more satisfying than spending 2 days coding to automate a 10-minute manual task?


If you're also lazy, overwhelmed by your musical chaos, and mildly addicted to automating everything, welcome — you’re among friends.

---

## 🚀 Features

- 🎵 Fetches your Spotify playlists using OAuth (yes, it’s safe)
- 🤖 Uses LLMs to guess the mood of each song
- 📊 Batch processing for large playlists
- 🧠 Built with FastAPI, Factory Pattern, Modular Routing 
- 🛠️ Easily extensible for more LLMs or music sources


---


## 🛠️ How to Run It

1. Clone the repo  

```bash
git clone https://github.com/your-username/MoodyTunes.git
cd MoodyTunes
```

2. Create and activate a virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```
3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Set up your .env file with required keys(mentioned in next stage)

5. Run the FastAPI server

```bash
uvicorn main:app --reload
```

6. Open your browser and go to http://localhost:8000/docs to test it out



---

## 🧪 .env Configuration

Create a `.env` file in your root directory and populate the following keys:

```env
# Spotify API Credentials
SPOTIPY_CLIENT_ID=your_spotify_client_id
SPOTIPY_CLIENT_SECRET=your_spotify_client_secret
SPOTIPY_REDIRECT_URI=http://127.0.0.1:8000/api/v1/auth/callback  # callback logic is handled in this endpoint 

# Gemini API Key
GEMINI_API_KEY=your_gemini_api_key

# Optional: LastFM API Key (if integrated later)
LASTFM_API_KEY=your_lastfm_api_key 

```
---

## Contributions

Contributions welcome! Feel free to open an issue or PR.