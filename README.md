Multi-Agent Customer Support System - A2A Orchestration with Strands Agents
An intelligent, empathetic customer support platform powered by AWS Bedrock and Claude 3.5 Sonnet, built using the Strands Agents framework and Agent-to-Agent (A2A) protocol. This system simulates a full support team by orchestrating four specialized AI agents that work in parallel to understand, analyze, and resolve customer queries.
🏗️ Architecture
This project follows a parallel multi-agent orchestration pattern using the official Strands Agents SDK and A2A protocol:
text┌─────────────────────────────────────────────────────────────┐
│                  Orchestrator Agent (Port 8000)              │
│          FastAPI + SSE Streaming UI + A2A Coordinator       │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────────┐
│  Intent      │ │    FAQ       │ │   Review     │ │   Solution     │
│  Agent       │ │   Agent      │ │   Agent      │ │   Agent        │
│ (Port 8001)  │ │ (Port 8002)  │ │ (Port 8003)  │ │ (Port 8004)    │
└──────────────┘ └──────────────┘ └──────────────┘ └────────────────┘
Agent Responsibilities

Intent Agent (Port 8001)
Classifies primary customer intent
Detects urgency level
Extracts order IDs and emotions
Provides summary of customer goal

FAQ Agent (Port 8002)
Handles common questions instantly
Returns policy, shipping, promotions
Escalates non-standard queries

Review Agent (Port 8003)
Analyzes sentiment and emotion
Detects profanity and legal threats
Determines escalation need
Extracts emotional key quotes

Solution Agent (Port 8004)
Provides empathetic, professional responses
Takes real actions: refunds, return labels, escalations
Thanks happy customers
Only uses tools when clearly required

Orchestrator Agent (Port 8000)
Coordinates all four agents via A2A protocol
Aggregates insights in parallel
Synthesizes final customer-facing response
Streams output with real-time typing effect


✨ Features

🤝 True Multi-Agent Collaboration: Parallel processing via A2A protocol
❤️ Human-Like Empathy: Final responses crafted by Claude 3.5 Sonnet
⚡ Real-Time Streaming: Smooth typing animation using Server-Sent Events
🛠️ Action-Oriented Tools: Fake but realistic refunds, escalations, return labels
🔍 Emotion & Urgency Aware: Profanity detection, threat escalation
📚 Smart FAQ Handling: Instant answers for common queries
🚀 Extensible Design: Easy to add new specialist agents

🚀 Tech Stack

Framework: Strands Agents SDK (official AWS open-source)
AI Model: Anthropic Claude 3.5 Sonnet via AWS Bedrock
Protocol: Agent-to-Agent (A2A) for inter-agent communication
Web Server: FastAPI + Uvicorn
Frontend: HTML + CSS + JavaScript with SSE streaming
Configuration: python-dotenv (.env file)
Cloud: AWS Bedrock (managed inference)

📋 Prerequisites

Python 3.10 or higher
AWS Account with Bedrock access
IAM credentials with bedrock:InvokeModel permissions
Ports 8000–8004 available

🔧 Installation

Clone the RepositoryBashgit clone https://github.com/your-username/multi-agent-customer-support.git
cd multi-agent-customer-support
Create Virtual EnvironmentBashpython -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
Install DependenciesBashpip install strands-agents strands-agents-tools fastapi uvicorn python-dotenv
Configure Environment
Create a .env file:Bashcp .env.example .envEdit .env with your AWS credentials:textBEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here

☁️ AWS Bedrock Setup

Enable model access in AWS Console → Bedrock → Model access
Request access to Anthropic Claude 3.5 Sonnet
Create IAM policy with bedrock:InvokeModel permission
Generate access keys and add to .env

🎯 Usage
Start all five processes (one per terminal):
Terminal 1: Intent Agent
Bashpython agents/intent_agent.py
Terminal 2: FAQ Agent
Bashpython agents/faq_agent.py
Terminal 3: Review Agent
Bashpython agents/reviewer_agent.py
Terminal 4: Solution Agent
Bashpython agents/solution_agent.py
Terminal 5: Orchestrator (Main UI)
Bashpython orchestrator/main.py
→ Automatically opens browser at http://127.0.0.1:8000
Start chatting! The system will respond empathetically with real actions when needed.
📡 API Endpoints

GET / → Web chat interface
GET /support?message=... → Streaming text response
GET /health → Health check

📁 Project Structure
textmulti-agent-customer-support/
├── agents/
│   ├── intent_agent.py      # Intent classification
│   ├── faq_agent.py         # FAQ handling
│   ├── reviewer_agent.py    # Sentiment & urgency analysis
│   └── solution_agent.py    # Action-taking senior agent
├── orchestrator/
│   └── main.py              # FastAPI orchestrator + UI
├── static/
│   └── ui.html              # Chat interface
├── .env                     # Credentials (git ignored)
├── .env.example            # Template
├── requirements.txt         # Dependencies
├── .gitignore
└── README.md                # This file
🔍 How It Works

Customer message → Orchestrator
Orchestrator uses A2A to call all 4 agents in parallel
Each agent uses specialized tools and returns structured insights
Orchestrator feeds everything to Claude 3.5 Sonnet
Final clean, empathetic response is streamed back with typing effect

🛠️ Development
Run orchestrator with auto-reload:
Bashuvicorn orchestrator.main:app --reload --host 127.0.0.1 --port 8000
🔒 Security Best Practices

Never commit .env file
Use minimal IAM permissions
Rotate credentials regularly
Consider AWS Secrets Manager for production

🤝 Contributing

Fork the repository
Create feature branch (git checkout -b feature/new-agent)
Commit changes (git commit -m 'Add new feature')
Push and open Pull Request

📄 License
MIT License - see LICENSE file for details.
🙏 Acknowledgments

Strands Agents SDK by AWS
Anthropic Claude via AWS Bedrock
FastAPI for modern web serving
Built in December 2025

Made with ❤️ for the future of AI customer support.
Live Demo: http://127.0.0.1:8000 (when running locally)
GitHub: https://github.com/your-username/multi-agent-customer-support
Ready to deploy your own AI support team? Start the agents and watch the magic! 🚀
