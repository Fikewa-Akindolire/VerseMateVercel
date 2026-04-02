from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from ._core import client, CHAT_MODES

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.post("/api/chat")
async def chat(request: Request):
    body        = await request.json()
    mode        = body.get("mode", "heart_check")
    messages    = body.get("messages", [])
    translation = body.get("translation", "ESV")

    system = CHAT_MODES.get(mode, CHAT_MODES["heart_check"])
    system += f"\n\nAlways use the {translation} translation when quoting Bible verses."

    max_tokens = 400 if len(messages) == 0 else 1500

    # Opening greeting trigger
    if len(messages) == 0:
        messages = [{"role": "user", "content":
            "Begin the conversation. Greet the user warmly in the voice of Jesus. "
            "Introduce VerseMate as a safe space. Ask one gentle opening question. "
            "Speak directly to them in first person as Jesus."}]

    resp = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=max_tokens,
        system=system,
        messages=messages
    )
    return JSONResponse({"reply": resp.content[0].text})