# API Documentation

<!--
Letta Chatbot API Documentation
Copyright (C) 2025 Letta Chatbot Contributors
Licensed under CC-BY-SA 4.0
-->

Complete API reference for the Letta Chatbot Flask application.

## Table of Contents

- [Authentication](#authentication)
- [Frontend Routes](#frontend-routes)
- [Agent Routes](#agent-routes)
- [Message Routes](#message-routes)
- [Runtime Routes](#runtime-routes)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)

## Authentication

The API uses cookie-based session authentication when `USE_COOKIE_BASED_AUTHENTICATION` is enabled.

### Session Cookie

- **Name**: `letta_uid`
- **Duration**: 24 hours
- **Scope**: Per-user isolation of agents and messages

### Disabling Authentication

Set `USE_COOKIE_BASED_AUTHENTICATION=false` to use a shared "default" user for all requests.

## Frontend Routes

### Get Main Chat Interface

```http
GET /
```

Renders the main chat interface with no agent selected.

**Response**: HTML page

---

### Get Chat with Specific Agent

```http
GET /<agent_id>
```

Renders the chat interface with the specified agent selected.

**Parameters**:
- `agent_id` (path): The ID of the agent to chat with

**Response**: HTML page

---

### Get Agent Details Component

```http
GET /agents/<agent_id>/details
```

Returns the agent details component for HTMX updates.

**Parameters**:
- `agent_id` (path): The ID of the agent

**Response**: HTML component

**Example**:
```html
<!-- HTMX automatically loads this when agent is selected -->
<div hx-get="/agents/agent-123/details" hx-trigger="load">
  <!-- Agent details rendered here -->
</div>
```

---

### Get Archival Memory Component

```http
GET /agents/<agent_id>/archival_memory
```

Returns the archival memory component for the specified agent.

**Parameters**:
- `agent_id` (path): The ID of the agent
- `query` (query, optional): Search query for filtering memories

**Response**: HTML component with archival memory passages

---

## Agent Routes

All agent routes are prefixed with `/api`.

### List Agents

```http
GET /api/agents
```

Get a list of all agents for the current user.

**Query Parameters**:
- None

**Response**:
```json
[
  {
    "id": "agent-123",
    "name": "My Agent",
    "created_at": "2025-01-15T09:30:00Z",
    "updated_at": "2025-01-15T10:00:00Z",
    "tags": ["user:abc123"],
    "memory_blocks": [
      {
        "label": "persona",
        "value": "I am a helpful assistant"
      }
    ]
  }
]
```

**Status Codes**:
- `200 OK`: Success
- `400 Bad Request`: User ID missing
- `500 Internal Server Error`: Server error

**HTMX Support**: Returns HTML component when `HX-Request` header is present

**Caching**: Results cached for 60 seconds

---

### Create Agent

```http
POST /api/agents
```

Create a new agent with default configuration.

**Request Body**: None (uses defaults from `default-agent.json`)

**Response**:
```json
{
  "id": "agent-456",
  "name": "New Agent",
  "created_at": "2025-01-15T09:30:00Z",
  "memory_blocks": [
    {
      "label": "human",
      "value": "The human's name is User"
    },
    {
      "label": "persona",
      "value": "My name is Sam"
    }
  ],
  "tags": ["user:abc123"]
}
```

**Status Codes**:
- `200 OK`: Agent created successfully
- `400 Bad Request`: User ID missing
- `500 Internal Server Error`: Creation failed

**Rate Limiting**: Subject to API rate limits

---

### Get Agent

```http
GET /api/agents/<agent_id>
```

Get details for a specific agent.

**Parameters**:
- `agent_id` (path): The ID of the agent

**Response**:
```json
{
  "id": "agent-123",
  "name": "My Agent",
  "system_prompt": "You are a helpful assistant",
  "memory_blocks": [...],
  "llm_config": {
    "model": "gpt-4",
    "temperature": 0.7
  }
}
```

**Status Codes**:
- `200 OK`: Success
- `400 Bad Request`: User ID missing
- `404 Not Found`: Agent not found or not owned by user
- `500 Internal Server Error`: Server error

**Ownership**: Validates that the agent belongs to the requesting user

---

### Update Agent

```http
PUT /api/agents/<agent_id>
```

Update an existing agent.

**Parameters**:
- `agent_id` (path): The ID of the agent

**Request Body**:
```json
{
  "name": "Updated Agent Name",
  "system_prompt": "New system prompt",
  "memory_blocks": [
    {
      "label": "persona",
      "value": "Updated persona"
    }
  ]
}
```

**Response**:
```json
{
  "id": "agent-123",
  "name": "Updated Agent Name",
  ...
}
```

**Status Codes**:
- `200 OK`: Agent updated successfully
- `400 Bad Request`: Invalid request data
- `404 Not Found`: Agent not found
- `500 Internal Server Error`: Update failed

---

### Delete Agent

```http
DELETE /api/agents/<agent_id>
```

Delete an agent.

**Parameters**:
- `agent_id` (path): The ID of the agent

**Response**:
```json
{
  "message": "Agent deleted successfully"
}
```

**Status Codes**:
- `200 OK`: Agent deleted successfully
- `400 Bad Request`: User ID missing
- `404 Not Found`: Agent not found
- `500 Internal Server Error`: Deletion failed

**Note**: This operation is irreversible and deletes all associated messages.

---

## Message Routes

### List Messages

```http
GET /api/agents/<agent_id>/messages
```

Get all messages for an agent's conversation.

**Parameters**:
- `agent_id` (path): The ID of the agent
- `limit` (query, optional): Maximum number of messages to return
- `before` (query, optional): Cursor for pagination

**Response**:
```json
[
  {
    "id": "msg-123",
    "role": "user",
    "content": "Hello!",
    "created_at": "2025-01-15T09:30:00Z"
  },
  {
    "id": "msg-124",
    "role": "assistant",
    "content": "Hi there! How can I help?",
    "created_at": "2025-01-15T09:30:05Z"
  }
]
```

**Status Codes**:
- `200 OK`: Success
- `400 Bad Request`: User ID missing
- `404 Not Found`: Agent not found
- `500 Internal Server Error`: Server error

**HTMX Support**: Returns HTML component when `HX-Request` header is present

**Message Filtering**: Automatically filters out system messages and internal messages

---

### Send Message

```http
POST /api/agents/<agent_id>/messages
```

Send a message to an agent and get a response.

**Parameters**:
- `agent_id` (path): The ID of the agent

**Request Body**:
```json
{
  "message": "What's the weather like?",
  "role": "user"
}
```

**Response**:
```json
{
  "messages": [
    {
      "id": "msg-125",
      "role": "user",
      "content": "What's the weather like?",
      "created_at": "2025-01-15T09:35:00Z"
    },
    {
      "id": "msg-126",
      "role": "assistant",
      "content": "I don't have real-time weather data...",
      "created_at": "2025-01-15T09:35:02Z"
    }
  ]
}
```

**Status Codes**:
- `200 OK`: Message sent successfully
- `400 Bad Request`: Invalid message or user ID missing
- `404 Not Found`: Agent not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

**HTMX Support**: Returns HTML messages when `HX-Request` header is present

**Rate Limiting**: Maximum 10 messages per minute per user

**Validation**:
- Message content must not be empty
- Maximum message length enforced
- XSS prevention applied

---

### Send Message (Streaming)

```http
POST /api/agents/<agent_id>/messages/stream
```

Send a message and receive streaming response via Server-Sent Events.

**Parameters**:
- `agent_id` (path): The ID of the agent

**Request Body**: Same as Send Message

**Response**: Server-Sent Events stream

**Event Types**:
- `message`: Partial message content
- `done`: Stream complete
- `error`: Error occurred

**Example**:
```javascript
const eventSource = new EventSource('/api/agents/agent-123/messages/stream');
eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Handle streaming data
};
```

---

## Runtime Routes

### Get Runtime Info

```http
GET /api/runtime
```

Get runtime configuration information.

**Response**:
```json
{
  "LETTA_BASE_URL": "https://your-server.com:8283"
}
```

**Status Codes**:
- `200 OK`: Success

**Use Case**: Frontend uses this to determine Letta server endpoint

---

## Error Handling

All API errors follow a consistent format:

```json
{
  "error": "Error description",
  "details": "Additional error details",
  "code": "ERROR_CODE"
}
```

### Common Error Codes

| Code | Description |
|------|-------------|
| `USER_ID_REQUIRED` | Authentication required |
| `AGENT_NOT_FOUND` | Agent does not exist |
| `INVALID_REQUEST` | Request validation failed |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `SERVER_ERROR` | Internal server error |

### HTTP Status Codes

| Status | Meaning |
|--------|---------|
| `200` | Success |
| `400` | Bad Request - Invalid input |
| `401` | Unauthorized - Authentication required |
| `404` | Not Found - Resource doesn't exist |
| `429` | Too Many Requests - Rate limited |
| `500` | Internal Server Error - Server error |

### Error Response Example

```json
{
  "error": "Agent not found",
  "details": "The agent with ID 'agent-123' does not exist or you don't have permission to access it",
  "code": "AGENT_NOT_FOUND"
}
```

---

## Rate Limiting

### Limits

- **API Endpoints**: 60 requests per minute per user
- **Message Endpoints**: 10 requests per minute per user

### Rate Limit Headers

Responses include rate limit information:

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1642349400
```

### Rate Limit Exceeded

When rate limit is exceeded, you receive:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 30

{
  "error": "Rate limit exceeded",
  "retry_after": 30
}
```

---

## Pagination

List endpoints support cursor-based pagination:

### Request

```http
GET /api/agents/<agent_id>/messages?limit=50&before=msg-100
```

### Response

```json
{
  "data": [...],
  "pagination": {
    "has_more": true,
    "next_cursor": "msg-50",
    "prev_cursor": null
  }
}
```

---

## Caching

### Cache Headers

Responses include caching headers:

```http
Cache-Control: public, max-age=60
ETag: "abc123"
```

### Cache Invalidation

Caches are automatically invalidated when:
- Agent is updated or deleted
- New message is sent
- Memory blocks are modified

---

## HTMX Integration

Many endpoints support HTMX for dynamic updates:

### HTMX Request Detection

Server detects HTMX requests via the `HX-Request` header and returns HTML instead of JSON.

### HTMX Response Headers

```http
HX-Trigger: agentUpdated
HX-Refresh: true
```

### Example HTMX Usage

```html
<button 
  hx-post="/api/agents" 
  hx-target="#agents-list"
  hx-swap="beforeend">
  Create Agent
</button>
```

---

## WebSocket Support

**Status**: Not yet implemented

Planned WebSocket endpoints for real-time updates:

- `ws://localhost:5000/ws/agents/<agent_id>/messages` - Real-time message stream
- `ws://localhost:5000/ws/agents` - Agent list updates

---

## Examples

### Creating and Chatting with an Agent (Python)

```python
import requests

# Create session
session = requests.Session()
base_url = "http://localhost:5000"

# Create agent
response = session.post(f"{base_url}/api/agents")
agent = response.json()
agent_id = agent['id']

# Send message
message_data = {
    "message": "Hello, how are you?",
    "role": "user"
}
response = session.post(
    f"{base_url}/api/agents/{agent_id}/messages",
    json=message_data
)
messages = response.json()['messages']

print(messages[-1]['content'])  # Print agent's response
```

### Creating and Chatting with an Agent (JavaScript)

```javascript
// Create agent
const createResponse = await fetch('/api/agents', {
  method: 'POST',
  credentials: 'include'
});
const agent = await createResponse.json();

// Send message
const messageResponse = await fetch(`/api/agents/${agent.id}/messages`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({
    message: 'Hello!',
    role: 'user'
  })
});
const { messages } = await messageResponse.json();

console.log(messages[messages.length - 1].content);
```

---

**For more information, see the [main README](../README.md) or [Letta API Reference](letta-api-reference.md).**

