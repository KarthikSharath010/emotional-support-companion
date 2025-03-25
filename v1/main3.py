from fastapi.responses import HTMLResponse, JSONResponse
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from textblob import TextBlob
import openai
import os

# Initialize FastAPI app
app = FastAPI()

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI API key (Set yours here)
openai.api_key = "YOUR_OPENAI_API_KEY"

# Data model
class UserPost(BaseModel):
    emotion: str
    content: str

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index2.html", {"request": request})

@app.get("/share", response_class=HTMLResponse)
async def share_page(request: Request):
    return templates.TemplateResponse("share.html", {"request": request})

@app.get("/community", response_class=HTMLResponse)
async def community_page(request: Request):
    return templates.TemplateResponse("community.html", {"request": request})

@app.post("/generate_response")
async def generate_response(post: UserPost):
    content = post.content.strip()

    # Sentiment analysis (optional - can influence prompt)
    blob = TextBlob(content)
    polarity = blob.sentiment.polarity

    # Dynamic Prompt Creation
    sentiment = "positive" if polarity > 0.3 else "neutral or negative"
    prompt = f"""
    The user just shared: "{content}"
    Their sentiment seems {sentiment}.
    Suggest three unique, helpful, and thoughtful things they could do next, based on their current mood.
    """

    # Call OpenAI API
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150,
        n=1,
        temperature=0.8
    )

    suggestions_text = response['choices'][0]['message']['content']

    return JSONResponse(content={
        "suggestions": suggestions_text
    })
