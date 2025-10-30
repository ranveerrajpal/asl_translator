from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# CORS setup (so your friend’s site can POST data)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static videos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Store incoming messages temporarily in memory
messages = []

# ASL video dictionary
asl_videos = {
    "hello": "hello.mp4",
    "how": "how.mp4",
    "are": "are.mp4",
    "you": "you.mp4",
    "thank": "thank.mp4"
}

def find_asl_video(word):
    """Return video path if exists, else None"""
    return f"/static/{asl_videos[word]}" if word in asl_videos else None


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    return FileResponse("index.html")


@app.post("/receive_text/")
async def receive_text(request: Request):
    """
    Endpoint to receive random words/sentences from your friend's website.
    Example JSON:
    {"message": "hello how are you"}
    """
    data = await request.json()
    text = data.get("message", "").strip()
    if not text:
        return {"status": "error", "detail": "No text received"}

    # Save message with possible ASL mappings
    words = text.lower().split()
    asl_matches = []
    for word in words:
        video = find_asl_video(word)
        if video:
            asl_matches.append({"word": word, "video": video})

    messages.append({"text": text, "asl": asl_matches})
    return {"status": "success", "received": text}


@app.get("/get_messages/")
async def get_messages():
    """Returns all received messages + any ASL videos"""
    return JSONResponse(content={"messages": messages})


if __name__ == "__main__":
 import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

