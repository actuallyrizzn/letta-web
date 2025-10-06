# Quick Deployment Reference

This is a quick reference for deploying the Letta Chatbot. For detailed information, see [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## Development vs Production

The application uses a **single unified WSGI entry point** (`wsgi.py`) that adapts based on the `FLASK_ENV` environment variable.

### Development Mode

```bash
# Set environment
export FLASK_ENV=development

# Run directly (with debug mode)
python wsgi.py

# Or with Gunicorn
gunicorn -w 1 --reload wsgi:app
```

### Production Mode

```bash
# Set environment
export FLASK_ENV=production
export FLASK_SECRET_KEY="your-secure-secret-key"

# Run with Gunicorn (recommended)
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app

# Or with uWSGI
uwsgi --http :5000 --wsgi-file wsgi.py --callable app
```

## Environment Variables

### Required for Production

```env
FLASK_ENV=production
FLASK_SECRET_KEY=your-secure-secret-key
LETTA_BASE_URL=https://your-letta-server.com:8283
LETTA_API_KEY=your_api_key
```

### Optional

```env
USE_COOKIE_BASED_AUTHENTICATION=true
CREATE_AGENTS_FROM_UI=true
PORT=5000
```

## Quick Commands

### Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run in development mode
FLASK_ENV=development python wsgi.py
```

### Production (systemd)

```bash
# Create service file at /etc/systemd/system/letta-chatbot.service
[Unit]
Description=Letta Chatbot
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/letta-chatbot
Environment="PATH=/var/www/letta-chatbot/venv/bin"
EnvironmentFile=/var/www/letta-chatbot/.env
ExecStart=/var/www/letta-chatbot/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 wsgi:app
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable letta-chatbot
sudo systemctl start letta-chatbot
```

### Docker

```bash
# Build
docker build -t letta-chatbot .

# Run
docker run -d -p 5000:5000 \
  -e FLASK_ENV=production \
  -e LETTA_BASE_URL=https://your-server.com:8283 \
  -e LETTA_API_KEY=your_key \
  -e FLASK_SECRET_KEY=your_secret \
  letta-chatbot
```

## Key Points

1. **Single Entry Point**: Use `wsgi.py` for all environments
2. **Environment Control**: Set `FLASK_ENV=development` or `FLASK_ENV=production`
3. **Default is Production**: For safety, defaults to production mode
4. **Never Run Debug in Production**: Debug mode is automatically disabled in production

## Testing the Setup

```bash
# Health check
curl http://localhost:5000/api/runtime

# Should return JSON with runtime info
```

For more details, see the [full deployment guide](docs/DEPLOYMENT.md).

