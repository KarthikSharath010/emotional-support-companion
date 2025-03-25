import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import google.generativeai as genai
import os

app = FastAPI()

# ✅ Serve static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ✅ Configure Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("❌ GEMINI_API_KEY not found! Set it using environment variables.")

genai.configure(api_key=GEMINI_API_KEY)

# ✅ Use Correct AI Model
MODEL_NAME = "models/gemini-1.5-pro-latest"

# ✅ Define API Request Model
class UserStory(BaseModel):
    content: str

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/share", response_class=HTMLResponse)
async def share_page(request: Request):
    return templates.TemplateResponse("share.html", {"request": request})

@app.get("/community", response_class=HTMLResponse)
async def community_page(request: Request):
    return templates.TemplateResponse("community.html", {"request": request})

# ✅ AI API Endpoint for Story Analysis (Primary)
@app.post("/api/posts")
async def analyze_story(story: UserStory):
    return await process_ai_response(story.content)

# ✅ Additional AI API Endpoint (Alternative)
@app.post("/api/analyze_story")
async def analyze_story_alternative(story: UserStory):
    return await process_ai_response(story.content)

# ✅ Function to Process AI Response
async def process_ai_response(content: str):
    try:
        content = content.strip()
        if not content:
            raise HTTPException(status_code=400, detail="Content cannot be empty")

        # ✅ Generate AI Prompt
        prompt = f"""
        You are an empathetic assistant.
        Read the following story and classify it as 'happy' or 'sad'. 
        If the story is sad, provide a consoling message. 
        If it's happy, give a congratulatory message.

        Story: {content}
        """

        # ✅ Call Gemini AI Model
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)

        # ✅ Handle AI Response
        ai_text = response.text.strip() if hasattr(response, "text") and response.text else "No response from AI."

        # ✅ Save AI Response to JSON
        ai_result = {"story": content, "ai_response": ai_text}
        with open("static/ai_response.json", "w") as f:
            json.dump(ai_result, f, indent=4)

        return JSONResponse(content=ai_result)
    
    except Exception as e:
        print(f"⚠️ Backend Error: {e}")
        raise HTTPException(status_code=500, detail="AI processing failed.")

# ✅ Endpoint to Save AI Response
@app.post("/api/save_response")
async def save_ai_response(response_data: dict):
    try:
        with open("static/ai_response.json", "w") as f:
            json.dump(response_data, f, indent=4)
        return JSONResponse(content={"message": "AI response saved successfully."})
    except Exception as e:
        print(f"⚠️ Save Response Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to save AI response.")

# ✅ Endpoint to Retrieve Saved AI Response
@app.get("/api/get_response", response_class=JSONResponse)
async def get_response():
    try:
        with open("static/ai_response.json", "r") as f:
            data = json.load(f)
        return JSONResponse(content=data)
    except FileNotFoundError:
        return JSONResponse(content={"error": "No AI response found."}, status_code=404)
