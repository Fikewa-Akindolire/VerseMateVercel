from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from ._core import client

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/api/daily-verse")
async def daily_verse():
    resp = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=200,
        system="You speak in the first-person voice of Jesus Christ. Speak directly to the reader.",
        messages=[{"role": "user", "content":
            "Give one short Bible verse for today and one sentence of encouragement spoken "
            "directly to the reader in the voice of Jesus. "
            "Format: VERSE: [reference and full text] | WORD: [one sentence encouragement in first person as Jesus]"}]
    )
    raw   = resp.content[0].text
    parts = raw.split("|")
    verse = parts[0].replace("VERSE:", "").strip() if parts else raw
    word  = parts[1].replace("WORD:",  "").strip() if len(parts) > 1 else ""
    return JSONResponse({"verse": verse, "word": word})