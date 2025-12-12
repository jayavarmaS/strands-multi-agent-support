# orchestrator/main.py
import os
import json
import asyncio
import logging
import threading
import time
import webbrowser
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, PlainTextResponse
from strands import Agent
from strands.models import BedrockModel
from strands_tools.a2a_client import A2AClientToolProvider
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AWS Bedrock setup
os.environ['AWS_ACCESS_KEY_ID'] = os.getenv('AWS_ACCESS_KEY_ID')
os.environ['AWS_SECRET_ACCESS_KEY'] = os.getenv('AWS_SECRET_ACCESS_KEY')
os.environ['AWS_DEFAULT_REGION'] = os.getenv('AWS_REGION', 'us-east-1')

app = FastAPI(title="Customer Support Assistant")

# Serve static files (your ui.html is here)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="static")

bedrock = BedrockModel(
    model_id=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0"),
    region_name=os.getenv("AWS_REGION", "us-east-1")
)

A2A_AGENT_URLS = [
    "http://127.0.0.1:8001",  # intent_agent
    "http://127.0.0.1:8002",  # faq_agent
    "http://127.0.0.1:8003",  # review_agent
    "http://127.0.0.1:8004",  # solution_agent
]

ORCHESTRATOR_SYSTEM_PROMPT = """You are an expert Customer Support Agent. Your job is to provide direct, helpful, empathetic responses to customers.

You have access to four specialized helper agents via tools:
- One classifies intent
- One handles FAQs
- One analyzes sentiment and urgency
- One suggests solutions

You MUST use the tools to gather information from all four agents first.

After receiving their outputs, your FINAL response to the user MUST be ONLY the customer-facing message — nothing else.

ABSOLUTE RULES FOR OUTPUT:
- Output ONLY the final response starting with "Dear Valued Customer," or similar greeting
- Do NOT include any internal thinking, tool calls, or analysis
- Do NOT include sections like:
  - INTENT CLASSIFICATION
  - FAQ MATCH & ANSWER
  - SENTIMENT & URGENCY ANALYSIS
  - RECOMMENDED SOLUTION
- Do NOT explain your process
- Do NOT output anything before or after the customer message

Your response should be:
- Warm and empathetic
- Professional and clear
- Structured with numbered steps when giving instructions
- End with an offer for more help
- Sign off with "Best regards, Customer Support Team"

Example of correct output only:
Dear Valued Customer,

I understand you're having difficulty creating a new email account...





That is ALL you output — nothing more."""

orchestrator = None

def create_orchestrator():
    global orchestrator
    try:
        logger.info("Initializing A2A client tools...")
        a2a_provider = A2AClientToolProvider(known_agent_urls=A2A_AGENT_URLS)
        orchestrator = Agent(
            model=bedrock,
            name="support_orchestrator",
            description="Multi-agent customer support orchestrator",
            system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
            tools=a2a_provider.tools
        )
        logger.info("Orchestrator initialized successfully")
    except Exception as e:
        logger.error(f"Failed to create orchestrator: {e}")
        raise

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("ui.html", {"request": request})

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "Customer Support Assistant"}

async def generate_response_stream(user_message: str):
    global orchestrator
    try:
        if orchestrator is None:
            yield f"data: {json.dumps({'type': 'status', 'message': 'Initializing agents...'})}\n\n"
            await asyncio.sleep(0.1)
            create_orchestrator()
            yield f"data: {json.dumps({'type': 'status', 'message': 'All agents ready!'})}\n\n"
            await asyncio.sleep(0.1)

        prompt = f"""User message: "{user_message}"

Use the tools to consult all four specialized agents about this customer query.
Then, provide ONLY the final, clean response to the customer — no internal sections, no analysis, just the direct message."""

        yield f"data: {json.dumps({'type': 'status', 'message': 'Agents are thinking...'})}\n\n"
        await asyncio.sleep(0.2)

        response = orchestrator(prompt)
        full_text = response.content if hasattr(response, 'content') else str(response)

        # Stream in small chunks for smooth typing effect
        chunk_size = 25
        for i in range(0, len(full_text), chunk_size):
            chunk = full_text[i:i + chunk_size]
            yield f"data: {json.dumps({'type': 'content', 'chunk': chunk})}\n\n"
            await asyncio.sleep(0.03)

        yield f"data: {json.dumps({'type': 'complete'})}\n\n"

    except Exception as e:
        logger.error(f"Error during generation: {e}")
        yield f"data: {json.dumps({'type': 'error', 'message': 'Sorry, something went wrong. Please try again.'})}\n\n"

@app.get("/support")
async def support(message: str = ""):
    if not message.strip():
        return PlainTextResponse("No message provided", status_code=400)
    return StreamingResponse(generate_response_stream(message.strip()), media_type="text/event-stream")

# Auto-open browser when running directly
def open_browser():
    time.sleep(2)  # Wait for server to start
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    # Open browser automatically
    threading.Thread(target=open_browser, daemon=True).start()
    
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
    
   