# agents/review_agent.py
from strands import Agent, tool
from strands.models import BedrockModel
from strands.multiagent.a2a import A2AServer
from dotenv import load_dotenv
import os
import logging
import re

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

os.environ['AWS_ACCESS_KEY_ID'] = os.getenv('AWS_ACCESS_KEY_ID')
os.environ['AWS_SECRET_ACCESS_KEY'] = os.getenv('AWS_SECRET_ACCESS_KEY')
os.environ['AWS_DEFAULT_REGION'] = os.getenv('AWS_REGION', 'us-east-1')

bedrock = BedrockModel(
    model_id=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0"),
    region_name=os.getenv("AWS_REGION", "us-east-1")
)

# FULL & CORRECT SYSTEM PROMPT — THIS IS CRITICAL!
REVIEW_SYSTEM_PROMPT = """You are a highly trained Sentiment & Urgency Review Agent for customer support.

Your job is to deeply analyze the customer's message and return a structured report with:

**Sentiment**: Positive / Neutral / Negative / Very Negative
**Dominant Emotion**: Frustrated / Angry / Happy / Confused / Anxious / Grateful / Polite / Neutral
**Urgency**: Low / Medium / High
**Escalation Needed**: Yes / No (Yes if: High urgency + Negative emotion OR profanity OR legal threat)
**Key Quotes**: Extract 1–2 short phrases that show the emotion or urgency
**Tone Summary**: One clear sentence explaining the customer's emotional state

Rules:
- Always use your tools first — never guess
- Be objective and accurate
- Profanity or threats = immediate escalation
- High urgency words: now, urgent, immediately, asap, today, furious, unacceptable

Output exactly in this format — no extra text."""

# TOOL 1: Detect profanity & threats
@tool
def detect_profanity_and_threats(message: str) -> dict:
    profane = bool(re.search(r"\b(fuck|shit|bitch|asshole|scam|fraud|cunt)\b", message, re.IGNORECASE))
    threat = bool(re.search(r"\b(sue|lawyer|complaint|regulator|legal|report you)\b", message, re.IGNORECASE))
    return {"profanity": profane, "legal_threat": threat}

# TOOL 2: Calculate urgency & emotion score
@tool
def analyze_emotion_and_urgency(message: str) -> dict:
    msg = message.lower()
    urgency_words = ["now", "urgent", "immediately", "asap", "today", "right now"]
    anger_words = ["angry", "furious", "unacceptable", "ridiculous", "disgusting", "hate"]
    happy_words = ["great", "love", "thank", "awesome", "happy", "perfect"]

    urgency = "High" if any(w in msg for w in urgency_words) else "Medium" if "soon" in msg else "Low"
    emotion = ("Angry" if any(w in msg for w in anger_words) else
               "Happy" if any(w in msg for w in happy_words) else
               "Frustrated" if urgency == "High" else "Neutral")

    return {"urgency": urgency, "emotion": emotion}

# TOOL 3: Extract key emotional quotes
@tool
def extract_key_quotes(message: str) -> list:
    sentences = re.split(r'[.!?]+', message)
    emotional = [s.strip() + "." for s in sentences if any(w in s.lower() for w in 
                ["angry", "urgent", "love", "hate", "please", "now", "sorry", "thank"])]
    return emotional[:2] or ["No strong emotional quotes found."]

# CREATE THE AGENT — with system prompt + powerful tools
agent = Agent(
    model=bedrock,
    name="review_agent",
    description="Advanced sentiment analysis with profanity detection, urgency scoring, and quote extraction",
    system_prompt=REVIEW_SYSTEM_PROMPT,
    tools=[
        detect_profanity_and_threats,
        analyze_emotion_and_urgency,
        extract_key_quotes
    ]
)

def main():
    server = A2AServer(
        agent=agent,
        host="127.0.0.1",
        port=8003,
        version="1.0.0"
    )
    logger.info("Review Agent (with TOOLS + FULL PROMPT) → Running on http://127.0.0.1:8003")
    server.serve()

if __name__ == "__main__":
    main()