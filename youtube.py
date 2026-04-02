from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import requests as req
from ._core import YOUTUBE_API_KEY

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.post("/api/youtube")
async def youtube(request: Request):
    body  = await request.json()
    query = body.get("query", "")
    if not YOUTUBE_API_KEY or not query:
        return JSONResponse({"videos": []})
    try:
        resp = req.get("https://www.googleapis.com/youtube/v3/search", params={
            "part": "snippet", "q": f"{query} sermon bible",
            "type": "video", "maxResults": 3, "key": YOUTUBE_API_KEY
        })
        items = resp.json().get("items", [])
        videos = [{"title":   i["snippet"]["title"],
                   "channel": i["snippet"]["channelTitle"],
                   "url":     f"https://www.youtube.com/watch?v={i['id']['videoId']}"}
                  for i in items]
        return JSONResponse({"videos": videos})
    except Exception:
        return JSONResponse({"videos": []})