# agents/intent_agent.py
from strands import Agent, tool
from strands.models import BedrockModel
from strands.multiagent.a2a import A2AServer
from dotenv import load_dotenv
import os
import re

load_dotenv()

bedrock = BedrockModel(
    model_id=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0"),
    region_name=os.getenv("AWS_REGION", "us-east-1")
)

INTENT_SYSTEM_PROMPT = """You are an expert Intent Classification agent for customer support.

Your task is to analyze the customer's message and classify:

**Primary Intent** (choose one main):
- Greeting / General Inquiry
- Product Information
- Billing / Payment Issue
- Refund Request
- Technical Support
- Account Issue
- Delivery / Shipping
- Complaint / Negative Feedback
- Feature Request
- Cancellation
- Praise / Positive Feedback
- Other

**Urgency Level**: Low / Medium / High
**Emotion Detected**: Neutral / Frustrated / Angry / Confused / Happy / Anxious / Polite

**Summary**: One short sentence describing the customer's goal.

Always use your tools first to extract order IDs and detect urgency.
Output in clean, structured format."""

@tool
def extract_order_id(message: str) -> str:
    match = re.search(r"(?:order|#)\s*#?(\w{4,})", message, re.IGNORECASE)
    return match.group(1) if match else "Not found"

@tool
def detect_urgency(message: str) -> str:
    if any(w in message.lower() for w in ["now", "urgent", "asap", "immediately", "today"]):
        return "High"
    if any(w in message.lower() for w in ["soon", "quickly"]):
        return "Medium"
    return "Low"

agent = Agent(
    model=bedrock,
    name="intent_agent",
    description="Classifies intent, urgency, emotion, and extracts order numbers",
    system_prompt=INTENT_SYSTEM_PROMPT,  # ← BACK AND STRONGER!
    tools=[extract_order_id, detect_urgency]
)

def main():
    server = A2AServer(agent=agent, port=8001)
    print("Intent Agent + Tools + System Prompt → Running on 8001")
    server.serve()

if __name__ == "__main__":
    main()