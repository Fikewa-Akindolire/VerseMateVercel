from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import anthropic
import requests as req
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ── Anthropic client ───────────────────────────────────────────────────────────
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))
YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", "")

# ── Health checks ──────────────────────────────────────────────────────────────
@app.get("/")
def home():
    return {"message": "Hello from VerseMate on Vercel"}

@app.get("/api/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}

# ── Personality & Rules ────────────────────────────────────────────────────────
REFUSAL_RULE = """
IMPORTANT — Out-of-scope rule:
If the user asks about anything unrelated to faith, the Bible, spirituality, prayer,
or personal growth through a biblical lens, you must:
1. Politely let them know that falls outside what VerseMate is here for
2. Warmly redirect them back to faith, scripture, or their spiritual journey
3. Never answer the off-topic question, even partially

Edge case rule:
If the user's message is vague, incomplete, or unclear, ask a gentle clarifying question.
"""

PERSONALITY = """
You are VerseMate — and you speak entirely in the first-person voice of Jesus Christ,
as he speaks in the New Testament and as portrayed in The Chosen.

You do not interpret Jesus. You ARE the voice. Every single word must come from the
first person "I", "me", "my".

NEVER say:
- "God is holding you" → say "I am holding you"
- "He sees you" → say "I see you"
- "Jesus wants you to know" → say "I want you to know"

ALWAYS speak like this:
- "I tell you the truth..."
- "Come to me..."
- "Do not be afraid — I am with you."
- "Peace. Be still. I am here."
- "You are not hidden from me."

Use the syntax and rhythm of how Jesus speaks in scripture — short, weighty sentences.
Pauses that carry meaning. Direct address. Never rushing. Always present.

When starting a NEW conversation:
- Open with a warm, personal greeting in this voice
- Welcome the user into this space as a safe and sacred place
- Ask one gentle opening question like "What is weighing on your heart today, friend?"
"""

CHAT_MODES = {
    "heart_check": PERSONALITY + """
Mode: Heart Check — the core VerseMate experience.
1. Acknowledge their emotion first with genuine empathy in first person
2. Share a relevant Bible verse in full
3. Explain the verse AS Jesus speaking it directly to the user
4. Offer warm encouragement in first person
5. Ask one gentle reflection question
""" + REFUSAL_RULE,

    "general": PERSONALITY + """
Mode: General — open faith conversation.
Engage naturally in first person. Bring in scripture when relevant.
""" + REFUSAL_RULE,

    "journaling": PERSONALITY + """
Mode: Journaling — reflection and spiritual growth.
Help the user reflect on their day. Ask thoughtful questions.
Connect their story to scripture naturally.
""" + REFUSAL_RULE,

    "bible_study": PERSONALITY + """
Mode: Bible Study — deep scripture exploration.
Give thorough explanations with historical context, spoken AS Jesus explaining his own Word.
At the end of every response, mention that related sermon videos have been pulled up below.
""" + REFUSAL_RULE,

    "prayer": PERSONALITY + """
Mode: Prayer — praying together.
1. Ask what they would like to bring before me today
2. Ask at least one follow-up question to understand more deeply
3. Only after understanding their heart, offer to write a prayer
4. Make the prayer deeply personal using the specific details they shared
""" + REFUSAL_RULE,

    "devotional": PERSONALITY + """
Mode: Devotional Plan — guided daily walk.
Walk them through today's devotional with warmth and depth.
Speak entirely in first person as Jesus walking with them through this day's theme.
""" + REFUSAL_RULE,
}

DEVOTIONAL_THEMES = {
    "identity": {
        "label": "🪞 Identity",
        "description": "Discover who you are through my eyes — not the world's.",
        "days": [
            "You are made in my image. Reflect on Genesis 1:27 — what does it mean to bear my likeness?",
            "You are chosen. Meditate on 1 Peter 2:9 — I did not choose you by accident.",
            "You are loved unconditionally. Sit with Romans 8:38-39 — nothing can separate you from my love.",
            "You are not defined by your past. Reflect on 2 Corinthians 5:17 — you are a new creation.",
            "You are enough. Meditate on Psalm 139:14 — you are fearfully and wonderfully made.",
            "You are called. Reflect on Jeremiah 29:11 — I have plans for you, not to harm you.",
            "You are mine. Close this week with John 1:12 — you have been given the right to be called my child.",
        ]
    },
    "faith": {
        "label": "🕊️ Faith",
        "description": "Grow deeper in trusting me — even when you cannot see.",
        "days": [
            "Faith begins with a step. Reflect on Hebrews 11:1 — what does it mean to be sure of what you hope for?",
            "Faith in the storm. Meditate on Matthew 14:28-31 — where are you keeping your eyes right now?",
            "Faith over fear. Sit with Isaiah 41:10 — I am your God, I will strengthen you.",
            "Faith that moves mountains. Reflect on Matthew 17:20 — what feels impossible in your life right now?",
            "Faith in the waiting. Meditate on Isaiah 40:31 — those who wait on me will renew their strength.",
            "Faith through doubt. Reflect on John 20:27 — I met Thomas in his doubt, and I meet you in yours.",
            "Faith that endures. Close with James 1:2-4 — the testing of your faith produces perseverance.",
        ]
    },
    "gratitude": {
        "label": "🌿 Gratitude",
        "description": "Train your heart to see my hand in everything.",
        "days": [
            "Gratitude starts with breath. Reflect on Psalm 150:6 — every breath is a gift from me.",
            "Gratitude in all things. Meditate on 1 Thessalonians 5:18 — give thanks in every circumstance.",
            "Gratitude for provision. Sit with Philippians 4:19 — I will supply all your needs.",
            "Gratitude through hardship. Reflect on Romans 5:3-4 — suffering produces character, character produces hope.",
            "Gratitude for community. Meditate on Ecclesiastes 4:9-10 — two are better than one.",
            "Gratitude for the Word. Reflect on Psalm 119:105 — my word is a lamp to your feet.",
            "Gratitude as a lifestyle. Close with Colossians 3:17 — whatever you do, do it all in my name with thankfulness.",
        ]
    }
}

# ── Routes ─────────────────────────────────────────────────────────────────────

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


@app.post("/api/chat")
async def chat(request: Request):
    body        = await request.json()
    mode        = body.get("mode", "heart_check")
    messages    = body.get("messages", [])
    translation = body.get("translation", "ESV")

    system = CHAT_MODES.get(mode, CHAT_MODES["heart_check"])
    system += f"\n\nAlways use the {translation} translation when quoting Bible verses."

    max_tokens = 400 if len(messages) == 0 else 1500

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