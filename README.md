<p align="center">
  <img src="https://img.shields.io/badge/Businessly-AI%20Business%20Automation-blueviolet?style=for-the-badge&logo=telegram" alt="Businessly">
</p>

<h1 align="center">🤖 Businessly</h1>

<p align="center">
  <strong>AI-powered business automation platform for Telegram</strong>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#tech-stack">Tech Stack</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#api">API</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.109-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/React-18-61DAFB?style=flat-square&logo=react&logoColor=black" alt="React">
  <img src="https://img.shields.io/badge/Vite-5-646CFF?style=flat-square&logo=vite&logoColor=white" alt="Vite">
  <img src="https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/GigaChat-Sber-21A038?style=flat-square&logo=sber&logoColor=white" alt="GigaChat">
</p>

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔐 **Secure Auth** | JWT authentication with bcrypt password hashing |
| 🤖 **Telegram Integration** | Connect multiple Telegram bots via BotFather tokens |
| 🧠 **AI Responses** | Automatic customer support powered by GigaChat AI |
| 💬 **Live Dashboard** | Real-time conversation monitoring and management |
| 🔄 **Smart Handoff** | AI automatically escalates complex queries to owners |
| 🛡️ **Security First** | Protection against SQL injection and XSS attacks |

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|------------|---------|
| ![Python](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white) | Core language |
| ![FastAPI](https://img.shields.io/badge/-FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white) | REST API framework |
| ![SQLAlchemy](https://img.shields.io/badge/-SQLAlchemy-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white) | Async ORM |
| ![SQLite](https://img.shields.io/badge/-SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white) | Database |
| ![JWT](https://img.shields.io/badge/-JWT-000000?style=flat-square&logo=jsonwebtokens&logoColor=white) | Authentication |

### Frontend
| Technology | Purpose |
|------------|---------|
| ![React](https://img.shields.io/badge/-React-61DAFB?style=flat-square&logo=react&logoColor=black) | UI framework |
| ![Vite](https://img.shields.io/badge/-Vite-646CFF?style=flat-square&logo=vite&logoColor=white) | Build tool |
| ![Axios](https://img.shields.io/badge/-Axios-5A29E4?style=flat-square&logo=axios&logoColor=white) | HTTP client |

### Integrations
| Service | Purpose |
|---------|---------|
| ![Telegram](https://img.shields.io/badge/-Telegram%20Bot%20API-26A5E4?style=flat-square&logo=telegram&logoColor=white) | Messaging platform |
| ![GigaChat](https://img.shields.io/badge/-GigaChat-21A038?style=flat-square&logo=sber&logoColor=white) | AI responses |

---

## 🚀 Installation

### Prerequisites
- Python 3.12+
- Node.js 18+
- [GigaChat API Key](https://developers.sber.ru/portal/products/gigachat-api)
- [ngrok](https://ngrok.com/) (for local development)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
npm run dev
```

---

## ⚙️ Configuration

Create `backend/.env` with:

```env
# Database
DATABASE_URL=sqlite+aiosqlite:///./businessly.db

# JWT (change in production!)
SECRET_KEY=your-super-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=60

# GigaChat API
GIGACHAT_AUTH_KEY=your-gigachat-auth-key
GIGACHAT_SCOPE=GIGACHAT_API_PERS

# Telegram Webhook (ngrok URL for local dev)
WEBHOOK_BASE_URL=https://your-ngrok-url.ngrok.io
```

---

## 📖 Usage

### 1. Create Account
Navigate to `http://localhost:3000/register`

### 2. Add Telegram Bot
1. Create bot via [@BotFather](https://t.me/BotFather)
2. Copy the token
3. Add bot in dashboard with business description

### 3. Activate Bot
Toggle the bot to active — webhook is set automatically

### 4. Start Chatting
Customers message your bot → AI responds automatically

### 5. Take Control
Switch to manual mode when needed from the dashboard

---

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/register` | Create account |
| `POST` | `/api/auth/login` | Get JWT token |
| `GET` | `/api/auth/me` | Current user info |

### Bots
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/bots/` | List user's bots |
| `POST` | `/api/bots/` | Add new bot |
| `PUT` | `/api/bots/{id}/toggle` | Start/stop bot |
| `DELETE` | `/api/bots/{id}` | Remove bot |

### Conversations
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/conversations/` | List conversations |
| `GET` | `/api/conversations/{id}/messages` | Get messages |
| `POST` | `/api/conversations/{id}/messages` | Send message |
| `PUT` | `/api/conversations/{id}/control` | Toggle AI/manual |

---

## 🔒 Security

- ✅ **SQL Injection**: SQLAlchemy ORM with parameterized queries
- ✅ **XSS**: Input sanitization (bleach + DOMPurify)
- ✅ **Passwords**: bcrypt hashing
- ✅ **Auth**: JWT with expiration
- ✅ **CORS**: Configured for frontend origin

---

## 📄 License

MIT License — feel free to use for your projects!

---

<p align="center">
  Made with ❤️ for business automation
</p>
