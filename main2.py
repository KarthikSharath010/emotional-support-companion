import json
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import google.generativeai as genai
import os

app = FastAPI()

# Serve static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Configure Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("❌ GEMINI_API_KEY not found! Set it using environment variables.")
genai.configure(api_key=GEMINI_API_KEY)

# Use Correct AI Model
MODEL_NAME = "models/gemini-1.5-pro-latest"

# Define API Request Model
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

# AI API Endpoint for Story Analysis
@app.post("/api/posts")
async def analyze_story(story: UserStory):
    return await process_ai_response(story.content)

# Endpoint to Retrieve Saved AI Responses
@app.get("/api/get_response", response_class=JSONResponse)
async def get_response():
    try:
        json_file_path = "static/ai_response.json"
        if os.path.exists(json_file_path):
            with open(json_file_path, "r") as f:
                data = json.load(f)
            return JSONResponse(content=data)
        else:
            return JSONResponse(content={"error": "No AI responses found."}, status_code=404)
    except Exception as e:
        print(f"⚠ Fetch Response Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve AI responses.")

# Function to Process AI Response and Append to JSON
async def process_ai_response(content: str):
    try:
        content = content.strip()
        if not content:
            raise HTTPException(status_code=400, detail="Content cannot be empty")

        # Generate AI Prompt with Suggestions
        prompt = f"""
        You are an empathetic assistant.
        If the story is sad, provide a consoling message. 
        If it's happy, give a congratulatory message.
        Story: {content}
        """

        # Call Gemini AI Model
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)

        # Handle AI Response
        ai_text = response.text.strip() if hasattr(response, "text") and response.text else "No response from AI."

        # Generate suggestions
        suggestion_prompt = f"Based on the following story, generate three actionable suggestions in 3 bullet points.\n\nStory: {content}"
        suggestion_response = model.generate_content(suggestion_prompt)
        suggestions_text = suggestion_response.text.strip() if hasattr(suggestion_response, "text") and suggestion_response.text else "No suggestions available."
        suggestions = suggestions_text.split("\n")[:3]  # Ensure exactly three suggestions

        ai_result = {"story": content, "ai_response": ai_text, "suggestions": suggestions}

        print("✅ AI response generated.")  # Debug log

        # Append AI Response to JSON File Instead of Overwriting
        json_file_path = "static/ai_response.json"
        try:
            with open(json_file_path, "r") as f:
                existing_data = json.load(f)
                if not isinstance(existing_data, list):
                    existing_data = []
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = []

        existing_data.append(ai_result)

        with open(json_file_path, "w") as f:
            json.dump(existing_data, f, indent=4)

        return JSONResponse(content=ai_result)

    except Exception as e:
        print(f"⚠ Backend Error: {e}")
        raise HTTPException(status_code=500, detail="AI processing failed.")

if __name__ == "_main_":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)