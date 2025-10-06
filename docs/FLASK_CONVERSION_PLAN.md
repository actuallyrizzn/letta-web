<!--
Letta Chatbot Flask Conversion Plan
Copyright (C) 2025 Mark Hopkins
Licensed under CC-BY-SA 4.0
-->

# Flask Conversion Project Plan

## Overview
Convert the Letta Chatbot Template from Next.js/React to Flask/Python while maintaining all functionality and improving deployment compatibility with LAMP/LEMP servers.

## Project Goals
- ✅ Deploy on traditional LAMP/LEMP servers
- ✅ Maintain all existing functionality
- ✅ Simplify deployment process
- ✅ Reduce complexity compared to Node.js stack
- ✅ Keep Letta server integration intact

## Architecture Analysis

### Current Stack
```
Frontend (React) → Next.js API Routes → Letta Server API
```

### Target Stack
```
Flask Templates/HTMX → Flask Routes → Letta Server API
```

## Phase 1: Backend API Conversion (Week 1)

### 1.1 Project Setup
- [ ] **Move existing Next.js code to `node/` subfolder**
- [ ] Create Flask project structure in project root
- [ ] Set up virtual environment
- [ ] Install dependencies (Flask, requests, python-dotenv)
- [ ] Create basic Flask app with routing
- [ ] Set up environment configuration

**Dependencies:**
```python
Flask==3.0.0
requests==2.31.0
python-dotenv==1.0.0
python-uuid==1.30
```

### 1.2 Core API Routes
Convert Next.js API routes to Flask routes:

#### `/api/agents` (GET, POST)
- [ ] Implement user session management
- [ ] Port agent listing with user filtering
- [ ] Port agent creation with default templates
- [ ] Add error handling and validation

#### `/api/agents/<agent_id>` (GET, PUT, DELETE)
- [ ] Port agent retrieval with ownership validation
- [ ] Port agent modification
- [ ] Port agent deletion
- [ ] Implement security checks

#### `/api/agents/<agent_id>/messages` (GET, POST)
- [ ] Port message listing with filtering
- [ ] Port message sending with streaming
- [ ] Handle real-time chat functionality
- [ ] Implement message filtering (remove system/heartbeat messages)

#### `/api/runtime` (GET)
- [ ] Port runtime configuration endpoint
- [ ] Return environment variables safely

### 1.3 Helper Functions
- [ ] Port user session management (`getUserId`, `getUserTagId`)
- [ ] Port agent ownership validation (`validateAgentOwner`)
- [ ] Port message filtering (`filterMessages`)
- [ ] Port Letta client configuration

### 1.4 Testing
- [ ] Create unit tests for API endpoints
- [ ] Test Letta server integration
- [ ] Validate error handling
- [ ] Test user session management

## Phase 2: Frontend Conversion (Week 2)

### 2.1 Template Structure
- [ ] Create base template with layout
- [ ] Set up Jinja2 templating
- [ ] Implement responsive design with Tailwind CSS
- [ ] Create component templates (sidebar, chat area, message composer)

### 2.2 Core Pages
- [ ] Convert main chat page (`/[agentId]/page.tsx`)
- [ ] Implement agent selection sidebar
- [ ] Create agent details panel
- [ ] Port message display components

### 2.3 Interactive Features
- [ ] Integrate HTMX for real-time updates
- [ ] Implement message streaming
- [ ] Add agent creation/deletion UI
- [ ] Port agent editing functionality

### 2.4 UI Components
Convert React components to Flask templates:

#### Sidebar Components
- [ ] `app-sidebar.tsx` → `sidebar.html`
- [ ] `app-sidebar-menu-button.tsx` → `sidebar_button.html`
- [ ] `app-sidebar-menu-message.tsx` → `sidebar_message.html`

#### Message Components
- [ ] `messages.tsx` → `messages.html`
- [ ] `message-composer.tsx` → `message_composer.html`
- [ ] `message.tsx` → `message.html`
- [ ] `reasoning-message.tsx` → `reasoning_message.html`

#### Agent Management
- [ ] `agent-details-display.tsx` → `agent_details.html`
- [ ] `edit-agent-form.tsx` → `edit_agent_form.html`
- [ ] `delete-agent-confirmation.tsx` → `delete_confirmation.html`

### 2.5 Real-time Features
- [ ] Implement Server-Sent Events (SSE) for message streaming
- [ ] Add WebSocket support for real-time updates (optional)
- [ ] Port optimistic UI updates with HTMX

## Phase 3: Advanced Features (Week 3)

### 3.1 Session Management
- [ ] Implement Flask-Session for user management
- [ ] Port cookie-based authentication
- [ ] Add session security features
- [ ] Implement user isolation

### 3.2 Error Handling & Validation
- [ ] Add comprehensive error handling
- [ ] Implement input validation with Flask-WTF
- [ ] Add CSRF protection
- [ ] Port error toast notifications

### 3.3 Performance Optimization
- [ ] Add caching for agent lists
- [ ] Implement message pagination
- [ ] Optimize database queries (if needed)
- [ ] Add request rate limiting

### 3.4 Mobile Responsiveness
- [ ] Ensure mobile compatibility
- [ ] Test responsive design
- [ ] Optimize touch interactions
- [ ] Test on various devices

## Phase 4: Deployment & Production (Week 4)

### 4.1 Production Configuration
- [ ] Set up production WSGI server (Gunicorn)
- [ ] Configure Nginx reverse proxy
- [ ] Set up SSL certificates
- [ ] Configure environment variables

### 4.2 LAMP/LEMP Integration
- [ ] Create deployment scripts
- [ ] Set up process management (systemd/PM2)
- [ ] Configure log rotation
- [ ] Set up monitoring

### 4.3 Docker Support (Optional)
- [ ] Create Dockerfile
- [ ] Set up docker-compose for development
- [ ] Create production Docker configuration
- [ ] Add health checks

### 4.4 Documentation
- [ ] Create deployment guide
- [ ] Document environment variables
- [ ] Add troubleshooting guide
- [ ] Create user manual

## Technical Specifications

### Flask Application Structure
```
letta-web/                      # Project root (Flask app)
├── node/                       # Original Next.js code (preserved)
│   ├── src/
│   ├── package.json
│   ├── next.config.ts
│   └── ... (all original files)
├── app/                        # Flask application
│   ├── __init__.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── agents.py
│   │   ├── messages.py
│   │   └── runtime.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── components/
│   │   └── partials/
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   ├── utils/
│   │   ├── letta_client.py
│   │   ├── session_manager.py
│   │   └── validators.py
│   └── config.py
├── tests/
├── requirements.txt
├── .env.example
├── wsgi.py
├── default-agent.json          # Shared configuration
└── README.md
```

### Environment Variables
```bash
# Required
LETTA_BASE_URL=http://localhost:8283
FLASK_SECRET_KEY=your-secret-key

# Optional
LETTA_API_KEY=your-api-key
USE_COOKIE_BASED_AUTHENTICATION=true
NEXT_PUBLIC_CREATE_AGENTS_FROM_UI=true
```

### Key Dependencies
```python
Flask==3.0.0
requests==2.31.0
python-dotenv==1.0.0
Flask-WTF==1.2.1
Flask-Session==0.5.0
gunicorn==21.2.0
```

## Risk Assessment

### High Risk
- **Streaming Implementation**: Real-time message streaming may be complex to implement with Flask
- **State Management**: Converting React state management to server-side sessions

### Medium Risk
- **UI Complexity**: Some React components may be difficult to replicate with templates
- **Performance**: Flask may not handle concurrent users as well as Next.js

### Low Risk
- **API Conversion**: Straightforward conversion of REST endpoints
- **Letta Integration**: Simple HTTP API calls

## Success Criteria

### Functional Requirements
- [ ] All original features work identically
- [ ] User sessions persist across browser restarts
- [ ] Real-time chat works smoothly
- [ ] Agent management functions properly
- [ ] Mobile responsiveness maintained

### Technical Requirements
- [ ] Deploys successfully on LAMP/LEMP server
- [ ] Performance comparable to original
- [ ] Security features maintained
- [ ] Error handling comprehensive

### Deployment Requirements
- [ ] Single command deployment
- [ ] Environment variable configuration
- [ ] Process management setup
- [ ] Monitoring and logging

## Timeline Summary

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| Phase 1 | Week 1 | Flask API backend |
| Phase 2 | Week 2 | Frontend templates |
| Phase 3 | Week 3 | Advanced features |
| Phase 4 | Week 4 | Production deployment |

**Total Estimated Time: 4 weeks**

## Next Steps

1. **Review and approve this plan**
2. **Move existing Next.js code to `node/` subfolder**
3. **Set up Flask development environment in project root**
4. **Begin Phase 1: Backend API Conversion**
5. **Create initial Flask project structure**
6. **Start with core API routes implementation**

## Repository Migration Notes

### Benefits of This Approach
- **Preserves original code** - Original Next.js implementation remains intact for reference
- **Clean separation** - Flask app in root, Node.js code in subfolder
- **Easy comparison** - Can reference original implementation during development
- **Rollback option** - Can easily revert to Node.js version if needed
- **Shared resources** - `default-agent.json` and other configs can be shared

### Migration Commands
```bash
# Move all existing files to node subfolder
mkdir node
mv src package.json next.config.ts tailwind.config.ts tsconfig.json components.json eslint.config.mjs postcss.config.mjs cypress node/

# Keep shared files in root
# default-agent.json, README.md, LICENSE, etc.
```

---

*This plan provides a comprehensive roadmap for converting the Letta Chatbot Template from Next.js to Flask while maintaining all functionality and improving deployment options.*
