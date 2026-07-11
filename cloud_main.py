"""
AIRA MVP Backend
-----------------
Handles:
  - Google Sign-In token verification
  - Chat endpoint (calls Gemini API)
  - Chat history storage per user

Run locally:
    pip install -r requirements.txt
    uvicorn cloud_main:app --reload

Deploy on Render:
    Start command -> uvicorn cloud_main:app --host 0.0.0.0 --port $PORT
    Set environment variables in Render dashboard:
        GOOGLE_CLIENT_ID = <your Google OAuth Web Client ID>
        XAI_API_KEY      = <your xAI (Grok) API key>
"""

import os
import requests
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from database import init_db, save_message, get_history, get_or_create_user

app = FastAPI(title="AIRA Backend")

# Allow your Flutter app (and testing tools) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
XAI_API_KEY = os.environ.get("XAI_API_KEY", "")
XAI_MODEL = os.environ.get("XAI_MODEL", "grok-4-fast")

init_db()


def verify_google_token(authorization: str = Header(...)) -> dict:
    """Reads 'Authorization: Bearer <id_token>' and verifies it with Google."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")

    token = authorization.replace("Bearer ", "").strip()
    try:
        idinfo = id_token.verify_oauth2_token(
            token, google_requests.Request(), GOOGLE_CLIENT_ID
        )
        return {
            "user_id": idinfo["sub"],
            "email": idinfo.get("email", ""),
            "name": idinfo.get("name", ""),
        }
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired Google token")


@app.get("/")
def root():
    return {"status": "AIRA backend is running"}


@app.post("/chat")
def chat(payload: dict, user: dict = Depends(verify_google_token)):
    message = (payload.get("message") or "").strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message is empty")

    get_or_create_user(user["user_id"], user["email"], user["name"])
    save_message(user["user_id"], "user", message)

    reply = call_grok(message)

    save_message(user["user_id"], "assistant", reply)
    return {"reply": reply}


@app.get("/history")
def history(user: dict = Depends(verify_google_token)):
    return {"messages": get_history(user["user_id"])}


def call_grok(message: str) -> str:
    """Sends the message to xAI's Grok API (OpenAI-compatible) and returns the reply text."""
    if not XAI_API_KEY:
        return "AIRA isn't fully set up yet — add XAI_API_KEY on the server."

    url = "https://api.x.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {XAI_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": XAI_MODEL,
        "messages": [
            {"role": "system", "content": "You are AIRA, a helpful personal AI assistant."},
            {"role": "user", "content": message},
        ],
    }

    try:
        res = requests.post(url, headers=headers, json=body, timeout=30)
        res.raise_for_status()
        data = res.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Sorry, I had trouble responding just now. ({e})"