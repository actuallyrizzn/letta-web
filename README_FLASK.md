# Letta Chatbot - Flask Version

A Flask-based chatbot application that provides a web interface for interacting with Letta AI agents.

## Features

- **Multi-agent Support** - Create and manage multiple AI agents
- **Real-time Chat** - Interactive chat interface with HTMX
- **Agent Management** - Create, edit, and delete agents
- **Persistent Memory** - Agents remember conversations across sessions
- **Responsive Design** - Works on desktop and mobile devices
- **User Sessions** - Cookie-based user management

## Quick Start

### Prerequisites

- Python 3.8+
- Letta server running (local or cloud)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd letta-chatbot-example
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp env.example .env
   # Edit .env with your Letta server details
   ```

5. **Run the application**
   ```bash
   python wsgi.py
   ```

6. **Open in browser**
   ```
   http://localhost:5000
   ```

## Configuration

### Environment Variables

- `LETTA_BASE_URL` - URL of your Letta server (default: http://localhost:8283)
- `LETTA_API_KEY` - Your Letta API key (optional for local servers)
- `FLASK_SECRET_KEY` - Secret key for sessions (change in production)
- `USE_COOKIE_BASED_AUTHENTICATION` - Enable user sessions (default: true)

### Default Agent Configuration

Edit `default-agent.json` to customize default agent settings:

```json
{
  "DEFAULT_MEMORY_BLOCKS": [
    {
      "label": "human",
      "value": "The human's name is Bob the Builder"
    },
    {
      "label": "persona", 
      "value": "My name is Sam, the all-knowing sentient AI."
    }
  ],
  "DEFAULT_LLM": "letta/letta-free",
  "DEFAULT_EMBEDDING": "letta/letta-free"
}
```

## Architecture

### Backend (Flask)
- **API Routes** - RESTful endpoints for agent and message management
- **Session Management** - Cookie-based user authentication
- **Letta Integration** - HTTP client for Letta API communication

### Frontend (Templates + HTMX)
- **Jinja2 Templates** - Server-side rendering with component reuse
- **HTMX** - Real-time updates without page refreshes
- **Tailwind CSS** - Responsive styling and dark mode support
- **Alpine.js** - Lightweight JavaScript for interactivity

## API Endpoints

- `GET /` - Main chat interface
- `GET /<agent_id>` - Chat with specific agent
- `GET /api/agents` - List user's agents
- `POST /api/agents` - Create new agent
- `GET /api/agents/<id>` - Get agent details
- `PUT /api/agents/<id>` - Update agent
- `DELETE /api/agents/<id>` - Delete agent
- `GET /api/agents/<id>/messages` - Get agent messages
- `POST /api/agents/<id>/messages` - Send message to agent
- `GET /api/runtime` - Get runtime configuration

## Development

### Project Structure

```
app/
├── __init__.py          # Flask app factory
├── config.py            # Configuration classes
├── routes/              # API routes
│   ├── agents.py        # Agent management
│   ├── messages.py      # Message handling
│   ├── runtime.py       # Runtime info
│   └── frontend.py      # Frontend routes
├── templates/           # Jinja2 templates
│   ├── base.html        # Base template
│   ├── index.html       # Main chat page
│   └── components/      # Reusable components
├── utils/               # Utilities
│   ├── letta_client.py # Letta API client
│   ├── session_manager.py # User sessions
│   └── validators.py    # Message filtering
└── static/             # Static files
```

### Running Tests

```bash
python -m pytest tests/ -v
```

### Production Deployment

1. **Set production environment**
   ```bash
   export FLASK_ENV=production
   ```

2. **Use production WSGI server**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
   ```

3. **Configure reverse proxy** (Nginx/Apache)

## Comparison with Next.js Version

| Feature | Next.js | Flask |
|---------|---------|-------|
| **Frontend** | React + TypeScript | Jinja2 + HTMX |
| **State Management** | React Query | Server sessions |
| **Real-time Updates** | WebSocket/SSE | HTMX + SSE |
| **Deployment** | Vercel/Node.js | Any Python host |
| **Complexity** | High | Medium |
| **Performance** | Excellent | Good |

## License

Same as original Letta Chatbot Template.
