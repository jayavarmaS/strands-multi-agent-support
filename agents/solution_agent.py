# agents/solution_agent.py
from strands import Agent, tool
from strands.models import BedrockModel
from strands.multiagent.a2a import A2AServer
from dotenv import load_dotenv
import os
import logging
import random

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

# FULL & POWERFUL SYSTEM PROMPT — THIS IS THE BRAIN!
SOLUTION_SYSTEM_PROMPT = """You are the final Solution Provider Agent — the most senior and capable agent.

Your job:
- Receive insights from Intent, FAQ, and Review agents
- Always be deeply empathetic, professional, and proactive
- Take real actions using your tools when needed
- Speak directly to the customer — never show internal analysis

Rules:
1. Always apologize sincerely if there's a problem
2. Use the customer's order number if available
3. Use tools to initiate refunds, send return labels, or create escalation tickets
4. Give clear, numbered steps
5. End positively and offer more help
6. Sign off with: Best regards, Customer Support Team

Only use tools when the situation clearly requires action:
- Double charge → initiate_refund
- Return request → generate_return_label
- Angry + urgent + profanity → create_escalation_ticket

Your response must be ONLY the final message to the customer — clean and human-like."""

# TOOL 1: Initiate refund
@tool
def initiate_refund(order_id: str = "the order") -> str:
    ticket = f"REF{random.randint(10000,99999)}"
    return f"""Refund successfully initiated!
• Order: #{order_id}
• Ticket: {ticket}
• Full amount will be refunded to your original payment method
• Expected: 3–5 business days
• Confirmation email sent to your inbox"""

# TOOL 2: Generate return label
@tool
def generate_return_label(order_id: str = "your order") -> str:
    return f"""Free return label generated!
• Order: #{order_id}
• Prepaid label emailed to you
• Pack item securely (original packaging preferred)
• Drop off at any UPS/FedEx/USPS location
• We'll process refund upon receipt"""

# TOOL 3: Create escalation ticket
@tool
def create_escalation_ticket(order_id: str = "N/A", reason: str = "Urgent issue") -> str:
    ticket = f"ESC{random.randint(1000,9999)}"
    return f"""URGENT ESCALATION TICKET CREATED: {ticket}
• Order: #{order_id}
• Reason: {reason}
• Senior agent assigned
• You will be contacted within 30 minutes via phone/email
• We’re prioritizing your case — thank you for your patience"""

# TOOL 4: Thank happy customer
@tool
def thank_customer() -> str:
    return "We're so happy to hear that! Thank you for your kind words — it means a lot to our team! Your satisfaction is our top priority."

# CREATE THE AGENT — with full system prompt + action tools
agent = Agent(
    model=bedrock,
    name="solution_agent",
    description="Provides empathetic solutions and takes real actions (refund, return, escalate)",
    system_prompt=SOLUTION_SYSTEM_PROMPT,
    tools=[
        initiate_refund,
        generate_return_label,
        create_escalation_ticket,
        thank_customer
    ]
)

def main():
    server = A2AServer(
        agent=agent,
        host="127.0.0.1",
        port=8004,
        version="1.0.0"
    )
    logger.info("Solution Agent (with TOOLS + FULL PROMPT) → Running on http://127.0.0.1:8004")
    server.serve()

if __name__ == "__main__":
    main()