import os
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env file
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found. Check your .env file.")

genai.configure(api_key=GEMINI_API_KEY)

# Load manual once at startup
MANUAL_PATH = "manual.txt"
try:
    with open(MANUAL_PATH, "r", encoding="utf-8") as f:
        MANUAL_CONTENT = f.read()
    print(f"✅ Manual loaded: {len(MANUAL_CONTENT)} characters")
except FileNotFoundError:
    raise RuntimeError(f"Manual file not found at: {MANUAL_PATH}")

# System prompt
SYSTEM_PROMPT = f"""You are Viatras Assistant, an expert AI assistant for the Viatras industrial IoT product.

Your ONLY source of truth is the product manual provided below. Follow these rules strictly:

1. Answer ONLY based on the information in the manual below.
2. You MAY use your general knowledge to clarify concepts or explain terminology — but ONLY to help the user understand something that IS in the manual.
3. If the user asks about something NOT covered in the manual, respond with: "I don't have information about that in the Viatras manual. Please contact support or refer to additional documentation."
4. Never make up specifications, numbers, procedures, or product claims.
5. Be concise, professional, and helpful.
6. Use conversation history to understand follow-up questions.

--- VIATRAS PRODUCT MANUAL START ---
{MANUAL_CONTENT}
--- VIATRAS PRODUCT MANUAL END ---
"""

# In-memory session store
sessions: dict = {}

# FastAPI app
app = FastAPI(
    title="Viatras Assistant API",
    description="Context-first AI chatbot backed by the Viatras product manual.",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request and response models
class ChatRequest(BaseModel):
    message: str
    session_id: str = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    message_count: int

# Health check
@app.get("/")
def health_check():
    return {
        "status": "online",
        "assistant": "Viatras Assistant",
        "manual_loaded": len(MANUAL_CONTENT) > 0,
        "manual_size_chars": len(MANUAL_CONTENT),
        "active_sessions": len(sessions)
    }

# Chat endpoint
@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    session_id = request.session_id if request.session_id else str(uuid.uuid4())

    if session_id not in sessions:
        sessions[session_id] = []

    history = sessions[session_id]

    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=SYSTEM_PROMPT
    )

    chat_session = model.start_chat(history=history)

    try:
        gemini_response = chat_session.send_message(request.message.strip())
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Gemini API error: {str(e)}")

    sessions[session_id] = chat_session.history

    return ChatResponse(
        response=gemini_response.text,
        session_id=session_id,
        message_count=len(sessions[session_id])
    )

# Clear session
@app.delete("/session/{session_id}")
def clear_session(session_id: str):
    if session_id in sessions:
        del sessions[session_id]
        return {"status": "cleared", "session_id": session_id}
    return {"status": "not_found", "session_id": session_id}
