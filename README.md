# Operation Firewall 🔥

A comprehensive threat analysis and detection platform that uses AI-powered analysis to identify phishing, fraudulent transactions, and suspicious cryptocurrency wallets. Operation Firewall combines multiple AI models with RAG (Retrieval-Augmented Generation) to provide accurate, cross-validated threat assessments.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Architecture](#architecture)
- [Contributing](#contributing)
- [License](#license)

## Overview

Operation Firewall is designed to protect users and organizations from various cyber threats by analyzing:

1. **Email/Message Content** - Detects phishing attempts and social engineering attacks
2. **Financial Transactions** - Identifies anomalous spending patterns and potential fraud
3. **Cryptocurrency Wallets** - Analyzes blockchain activity for suspicious patterns

The platform uses a dual-validation approach: initial analysis with Backboard's RAG engine followed by cross-validation with Google Gemini to ensure accuracy and reduce false positives.

## ✨ Features

- **Multi-Threat Detection**
  - Phishing and social engineering detection
  - Transaction anomaly detection
  - Crypto wallet analysis
  
- **AI-Powered Analysis**
  - Backboard RAG integration for context-aware analysis
  - Google Gemini cross-validation for accuracy
  - Confidence scoring system
  
- **Threat Blocklisting**
  - Dynamic blocklist management
  - Automatic threat sender identification
  - Fast in-memory caching with Valkey
  
- **REST API**
  - RESTful endpoint for threat analysis
  - Health check and alert retrieval
  - Unified analyze endpoint for all entity types
  
- **Modern UI**
  - React + TypeScript frontend
  - Real-time threat analysis
  - Responsive design with Vite

## 🛠 Tech Stack

### Backend
- **Framework**: FastAPI 0.115.6
- **Server**: Uvicorn
- **Data Validation**: Pydantic 2.9.2
- **Database/Cache**: Valkey (Redis-compatible)
- **AI Integration**: 
  - Backboard SDK
  - Google GenAI
- **API Client**: httpx, requests
- **Config Management**: python-dotenv

### Frontend
- **Framework**: React 19.2.0
- **Build Tool**: Vite 7.3.1
- **Language**: TypeScript
- **Styling**: CSS

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Proxying**: Nginx
- **Cache/Database**: Valkey

## 📁 Project Structure

```
Team7_HackNC/
├── backend/                      # Python FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application & routes
│   │   ├── threat_analyzer.py   # Core threat analysis logic
│   │   ├── models.py            # Pydantic data models
│   │   ├── config.py            # Configuration management
│   │   ├── storage.py           # Data storage/retrieval
│   │   ├── risk_engine.py       # Risk scoring algorithms
│   │   ├── dbsetup.py           # Database initialization
│   │   ├── create_assistant.py  # AI assistant setup
│   │   ├── getassistantid.py    # Retrieve assistant ID
│   │   ├── upload.py            # File upload handling
│   │   ├── phishing_messages.txt # Training data
│   │   ├── integrations/
│   │   │   ├── backboard.py     # Backboard integration
│   │   │   └── gemini.py        # Google Gemini integration
│   ├── Dockerfile
│   ├── requirements.txt
│   └── testenv/                 # Python virtual environment
├── frontend/                     # React TypeScript frontend
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── App.css
│   │   ├── index.css
│   │   ├── lib/
│   │   │   └── api.ts           # API client
│   │   └── assets/
│   ├── public/
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.js
│   ├── tsconfig.json
│   └── eslint.config.js
├── docker-compose.yml            # Multi-container orchestration
├── nginx.conf                    # Nginx configuration
└── README.md
```

## 📋 Prerequisites

- Docker & Docker Compose (recommended)
- OR:
  - Python 3.8+
  - Node.js 18+
  - Valkey/Redis

## 🚀 Installation

### Option 1: Using Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Team7_HackNC
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Start all services**
   ```bash
   docker-compose up --build
   ```

The application will be available at:
- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Option 2: Manual Installation

#### Backend Setup

1. **Create and activate virtual environment**
   ```bash
   cd backend
   python -m venv testenv
   # On Windows:
   .\testenv\Scripts\activate
   # On macOS/Linux:
   source testenv/bin/activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Start Valkey (if not using Docker)**
   ```bash
   # Install and start Valkey/Redis
   valkey-server
   ```

5. **Run the backend**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

#### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**
   ```bash
   npm run dev
   ```

The frontend will be available at http://localhost:5173

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Backboard API Configuration
BACKBOARD_API_KEY=your_backboard_api_key

# Google Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key

# Valkey/Redis Configuration
VALKEY_HOST=valkey
VALKEY_PORT=6379

# Backend Configuration
ASSISTANT_ID=your_assistant_id
```

### API Keys Required

1. **Backboard API Key**
   - Sign up at Backboard platform
   - Generate API key from dashboard

2. **Google Gemini API Key**
   - Get from Google Cloud Console
   - Enable Generative AI API

## 🏃 Running the Application

### Using Docker Compose

```bash
# Start all services
docker-compose up

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### Development Mode

```bash
# Terminal 1: Backend
cd backend
source testenv/bin/activate  # or .\testenv\Scripts\activate on Windows
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Valkey
valkey-server
```

### Production Build

```bash
# Backend
docker build -t operation-firewall-backend ./backend

# Frontend
docker build -t operation-firewall-frontend ./frontend

# Run with docker-compose
docker-compose up
```

## 📚 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. Health Check
```
GET /health
```
**Response**:
```json
{
  "status": "ok",
  "ts": 1234567890
}
```

#### 2. Get Alerts
```
GET /alerts?limit=50
```
**Response**:
```json
{
  "alerts": []
}
```

#### 3. Analyze Entity
```
POST /analyze
```

**Request**:
```json
{
  "entity": "sender@example.com",
  "entity_type": "email",
  "context": {
    "body": "Click here for free money!",
    "message": "Suspicious email content"
  }
}
```

**Entity Types**:
- `email` - Email/message analysis
- `transaction` - Financial transaction analysis
- `wallet` - Cryptocurrency wallet analysis

**Response**:
```json
{
  "entity": "sender@example.com",
  "entity_type": "email",
  "risk_score": 85,
  "verdict": "block",
  "reasons": ["Known phishing pattern", "Suspicious sender"],
  "case_id": "case_12345",
  "cached": false,
  "ai_summary": "High confidence phishing attempt detected",
  "agreement": 0.95
}
```

**Risk Score Interpretation**:
- 0-33: Low risk (allow)
- 34-66: Medium risk (review)
- 67-100: High risk (block)

### Interactive API Documentation

Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc

## 🏗 Architecture

### System Flow

```
User Request → Frontend (React) 
    ↓
API Gateway (Nginx)
    ↓
FastAPI Backend
    ↓
Threat Analyzer
    ├→ Blocklist Check (Valkey)
    ├→ Backboard RAG Analysis
    └→ Gemini Cross-Validation
    ↓
Response with Risk Score & Verdict
    ↓
Frontend UI
```

### Data Flow

1. **Input**: User submits entity for analysis (email, transaction, wallet)
2. **Blocklist Check**: Valkey cache checked for known threats
3. **Primary Analysis**: Backboard performs RAG-based analysis with context
4. **Cross-Validation**: Google Gemini validates the analysis
5. **Scoring**: Confidence score converted to risk score (0-100)
6. **Blocklisting**: Low-confidence senders added to blocklist
7. **Output**: JSON response with verdict and confidence

## 🔄 Threat Analysis Process

### Message Analysis
1. Check sender against global blocklist
2. Query Backboard for similar messages (RAG)
3. Analyze text for social engineering patterns
4. Validate with Gemini
5. Update blocklist if confidence < 40%

### Transaction Analysis
1. Retrieve user's average spending from cache
2. Check if transaction exceeds threshold (10x average)
3. Query Backboard for similar transactions
4. Calculate anomaly score
5. Return risk assessment

### Crypto Wallet Analysis
1. Retrieve wallet transaction history
2. Query Backboard for wallet patterns
3. Analyze for suspicious activity
4. Cross-validate blockchain data
5. Generate risk assessment

## 🧪 Testing

### Manual API Testing

```bash
# Using curl
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "entity": "test@phishing.com",
    "entity_type": "email",
    "context": {"body": "urgent action needed"}
  }'
```

### Health Check
```bash
curl http://localhost:8000/health
```

## 🐛 Troubleshooting

### Issue: Connection refused to Valkey
- Ensure Valkey is running: `valkey-server`
- Check environment variables in `.env`
- Verify VALKEY_HOST and VALKEY_PORT settings

### Issue: API key errors
- Verify BACKBOARD_API_KEY is set correctly
- Verify GEMINI_API_KEY is set correctly
- Check API key permissions and quotas

### Issue: Frontend can't connect to backend
- Ensure backend is running on port 8000
- Check CORS settings in FastAPI
- Verify nginx.conf is correctly configured

### Issue: Docker containers won't start
```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# Rebuild containers
docker-compose build --no-cache
```

## 📝 Development Guidelines

### Adding New Analysis Types

1. Add new method to `ThreatAnalyzer` class in [threat_analyzer.py](backend/app/threat_analyzer.py)
2. Add entity type to `models.py`
3. Update `/analyze` endpoint in [main.py](backend/app/main.py)
4. Add frontend component for new analysis type

### Code Structure
- Keep AI logic in `threat_analyzer.py`
- Integrations in `integrations/` directory
- Data models in `models.py`
- Storage operations in `storage.py`

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Contributing

Team7 HackNC 2026

### Team Members
- Backend Development
- Frontend Development
- AI/ML Integration
- Infrastructure & DevOps

## 🚀 Future Enhancements

- Real-time threat feed integration
- Machine learning model training pipeline
- Multi-language support
- Advanced analytics dashboard
- Webhook support for alerts
- GraphQL API support
- Mobile application
- Blockchain integration improvements

---

**Last Updated**: February 2026  
**Version**: 0.1.0