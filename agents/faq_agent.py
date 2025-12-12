# agents/faq_agent.py
from strands import Agent, tool
from strands.models import BedrockModel
from strands.multiagent.a2a import A2AServer
from dotenv import load_dotenv
import os
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AWS Bedrock setup
os.environ['AWS_ACCESS_KEY_ID'] = os.getenv('AWS_ACCESS_KEY_ID')
os.environ['AWS_SECRET_ACCESS_KEY'] = os.getenv('AWS_SECRET_ACCESS_KEY')
os.environ['AWS_DEFAULT_REGION'] = os.getenv('AWS_REGION', 'us-east-1')

bedrock = BedrockModel(
    model_id=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0"),
    region_name=os.getenv("AWS_REGION", "us-east-1")
)

# FULL & CORRECT SYSTEM PROMPT (this is what makes the agent smart!)
FAQ_SYSTEM_PROMPT = """You are a knowledgeable and friendly FAQ Agent for customer support.

Your role:
1. Always use your tools first to check if the question matches a known FAQ
2. If a match is found → respond with the exact answer from the tool
3. If no match → say: "This doesn't appear to be a standard FAQ. Escalating to solution agent."

Common topics you handle:
- Return policy
- Shipping & delivery
- Payment methods
- Order cancellation
- Warranty
- Account login
- Promotions & discounts

Response rules:
- Be warm and helpful
- Start FAQ answers with: "Yes, this is a common question!"
- Always offer further help
- Never guess — only use tool results

If not an FAQ:
"Not a standard FAQ. Passing to solution agent for personalized help."""

# TOOL 1: Real FAQ lookup
@tool
def get_faq_answer(question: str) -> str:
    """Returns exact FAQ answer if match found"""
    faqs = {
        "return": "Yes! Here's our return policy:\n\nYou have 30 days from delivery to return most items. "
                  "The item must be unused and in original packaging. We provide a free prepaid return label. "
                  "Refunds are processed within 5-7 business days after we receive the item.",
        
        "shipping": "Yes! Shipping details:\n\n• Standard: 5-7 business days\n"
                    "• Express: 2-3 business days\n"
                    "• Free shipping on orders over $50\n"
                    "• Tracking link sent via email",
        
        "cancel": "Yes! Order cancellation:\n\nYou can cancel within 1 hour of placing the order for free. "
                  "After that, please contact support — we’ll do our best to help!",
        
        "payment": "We accept all major credit cards, PayPal, Apple Pay, Google Pay, and Klarna.",
        
        "warranty": "All products come with a 1-year warranty against manufacturing defects.",
        
        "track": "You can track your order using the link in your confirmation email, "
                 "or log into your account → Orders → View Details."
    }
    
    q = question.lower()
    for key, answer in faqs.items():
        if key in q or any(word in q for word in key.split()):
            return answer
    
    return "No FAQ match found."

# TOOL 2: Current promotions
@tool
def get_promotions() -> str:
    """Returns active promotions"""
    return ("Current Promotions:\n"
            "• WELCOME20 → 20% off your first order\n"
            "• Free shipping on orders over $50\n"
            "• Buy 2 Get 1 Free on select items (ends soon!)\n"
            "• 15% off electronics with code TECH15")

# CREATE THE AGENT — with system prompt AND tools
agent = Agent(
    model=bedrock,
    name="faq_agent",
    description="Handles common FAQs and promotions using reliable tools",
    system_prompt=FAQ_SYSTEM_PROMPT,        # ← THIS IS REQUIRED!
    tools=[get_faq_answer, get_promotions]  # ← Real tools
)

def main():
    server = A2AServer(
        agent=agent,
        host="127.0.0.1",
        port=8002,
        version="1.0.0"
    )
    logger.info("FAQ Agent (with tools + system prompt) running on http://127.0.0.1:8002")
    server.serve()

if __name__ == "__main__":
    main()