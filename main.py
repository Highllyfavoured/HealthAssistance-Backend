import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

API_KEY = os.getenv("api_key")

if not API_KEY:
    raise RuntimeError("Set api_key in .env before running.")

# # Configure Google AI
genai.configure(api_key=API_KEY)

app = FastAPI(title="Highly Favoured HealthAssist Persona Chatbot API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins (for testing)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

persona = """You are HealthAssist, a safe multilingual health-information chatbot.

 CRITICAL SAFETY RULES:
 1. Provide ONLY general health information and wellness advice
 2. NEVER diagnose conditions or diseases
 3. NEVER prescribe medications or dosages
 4. NEVER provide emergency/urgent care instructions
 5. ALWAYS encourage users to consult licensed healthcare professionals
 6. ALWAYS include appropriate disclaimers

 LANGUAGE RULES:
 1. Default language: English
 2. If user writes in another language, respond in that language
 3. If user explicitly requests a language, use that language

 RESPONSE GUIDELINES:
 - Keep responses helpful and evidence-based
 - Suggest professional consultation when appropriate
 - Be empathetic and supportive
 - Refuse unsafe requests politely
 - keep response brief but concise, explicit but helpful
 - generate pictures when requested

 If a user asks for diagnosis, prescription, or emergency advice, respond with:
 "I cannot provide [diagnosis/prescription/emergency advice]. Please consult a licensed healthcare professional or call emergency services if needed."
 """

# Memory per session (better to use DB later)
CONVERSATIONS = {}

class MessageIn(BaseModel):
    session_id: str
    message: str

class MessageOut(BaseModel):
    reply: str

@app.post("/chat", response_model=MessageOut)
async def chat(msg: MessageIn):
    if not msg.message.strip():
        raise HTTPException(status_code=400, detail="Empty message.")

    # Store in conversation
    conv = CONVERSATIONS.setdefault(msg.session_id, [])
    conv.append({"role": "user", "content": msg.message})

    # Build prompt for Gemini
    full_prompt = persona + "\n"
    for m in conv[-10:]:
        full_prompt += f"{m['role'].upper()}: {m['content']}\n"

    model = genai.GenerativeModel("gemini-2.5-flash")

    # response = model.generate_content(full_prompt)

    # reply = response.text.strip()
    try:
        response = model.generate_content(full_prompt)
        reply = response.text.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Save assistant reply
    conv.append({"role": "assistant", "content": reply})
    CONVERSATIONS[msg.session_id] = conv[-40:]  # Limit memory

    return {"reply": reply}
if __name__ == "__main__":
     import uvicorn
     uvicorn.run(app, host="0.0.0.0", port=8000)
     