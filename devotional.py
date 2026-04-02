from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from ._core import client, CHAT_MODES, DEVOTIONAL_THEMES

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/api/devotional/themes")
async def get_themes():
    return JSONResponse({k: {"label": v["label"], "description": v["description"]}
                         for k, v in DEVOTIONAL_THEMES.items()})

@app.post("/api/devotional/chat")
async def devotional_chat(request: Request):
    body     = await request.json()
    theme    = body.get("theme", "identity")
    day      = body.get("day", 0)
    messages = body.get("messages", [])

    info     = DEVOTIONAL_THEMES.get(theme, DEVOTIONAL_THEMES["identity"])
    day_text = info["days"][min(day, 6)]
    system   = CHAT_MODES["devotional"]

    if len(messages) == 0:
        messages = [{"role": "user", "content":
            f"Today's devotional theme is {info['label']}, Day {day+1}. "
            f"The focus is: {day_text}. Open this devotional session warmly in the voice of Jesus, "
            f"introduce the theme and scripture, and invite the user to reflect."}]
        max_tokens = 400
    else:
        max_tokens = 1000

    resp = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=max_tokens,
        system=system,
        messages=messages
    )
    return JSONResponse({"reply": resp.content[0].text, "day_text": day_text})