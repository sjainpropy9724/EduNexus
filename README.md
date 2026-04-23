![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![React](https://img.shields.io/badge/react-18.x-blue)
![Neo4j](https://img.shields.io/badge/neo4j-GraphDB-green)

# EduNexus v2

**A Knowledge Graph-Powered Platform for Skill Gap Analysis and Educational Alignment**

EduNexus v2 is an intelligent system that bridges the gap between industry skill demands and educational curricula. It leverages knowledge graphs, LLMs, and advanced NLP techniques to analyze job market trends, detect skill gaps, and provide actionable insights for educators and learners.

---

## 🎯 Features

- **Job Market Analysis**: Ingest and analyze DICE job postings to extract skill requirements
- **Curriculum Ingestion**: Process educational syllabi and extract learning outcomes
- **Skill Gap Detection**: Identify missing skills between market demand and educational offerings
- **Knowledge Graph**: Build and visualize skill relationships using Neo4j
- **LLM-Powered Parsing**: Extract structured information from unstructured job descriptions and syllabi
- **Market Simulation**: Simulate skill market evolution and track demand changes over time
- **Real-time Analytics**: Generate dynamic reports on skill trends and gaps
- **Interactive Visualization**: React-based frontend with graph visualization
- **Async Task Processing**: Celery-based background job processing for long-running operations

---

## 🏗️ Architecture

### Tech Stack

**Backend:**
- FastAPI - High-performance Python web framework
- Neo4j 5.15 - Knowledge graph database
- Redis 7.2 - Message broker & caching
- Celery 5.3 - Distributed task queue
- Anthropic Claude API - LLM for intelligent parsing
- Hugging Face - Pre-trained models for embeddings and NLP
- PDFPlumber - PDF document processing

**Frontend:**
- React 19 - UI library
- Vite - Lightning-fast build tool
- Tailwind CSS - Utility-first CSS framework
- React Force Graph 2D - Interactive graph visualization
- Axios - HTTP client

### Services Overview

```
Backend Services:
├── ingestion.py          # Document ingestion and indexing
├── llm_parser.py         # LLM-based parsing of jobs & syllabi
├── gap_analyzer.py       # Skill gap detection logic
├── graph_builder.py      # Neo4j knowledge graph construction
├── skill_normalizer.py   # Normalize & standardize skills
├── vector_store.py       # Vector embeddings & similarity search
├── report_generator.py   # Generate analysis reports
├── analytics.py          # Analytics and aggregations
└── tasks.py              # Celery task definitions
```

---

## 🚀 Quick Start

### Prerequisites

- Docker Desktop (for Neo4j and Redis)
- Python 3.10+
- Node.js 18+
- pip and npm

### Installation & Setup

#### 1. Start Services (Docker)

```bash
# From project root
docker-compose up -d

# This starts:
# - Neo4j at http://localhost:7475
# - Redis at localhost:6380
# - Flower (Celery UI) at http://localhost:5555
```

#### 2. Set up Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Build Knowledge Graph

```bash
# From backend directory with venv activated

# 1. Ingest job postings
python bulk_upload_jobs.py

# 2. Ingest syllabi (takes ~1 hour)
python bulk_upload_syllabus.py
```

#### 4. Set up Frontend

```bash
cd frontend
npm install
```

---

## 🏃 Running the Application

### Terminal 1: Backend API

```bash
cd backend
# Activate venv first (if not already)
uvicorn app.main:app --reload --port 8001
```

### Terminal 2: Celery Worker

```bash
cd backend
# Activate venv first
celery -A app.core.celery_app worker --loglevel=info -P solo
```

### Terminal 3: Celery Beat (Scheduler)

```bash
cd backend
# Activate venv first
celery -A app.core.celery_app beat --loglevel=info
```

### Terminal 4: Market Simulator (Optional)

```bash
cd backend
# Activate venv first
python simulate_market.py
```

### Terminal 5: Frontend Development Server

```bash
cd frontend
npm run dev -- --port 5174
```

### Access the Application

- **Frontend**: http://localhost:5174
- **Backend API**: http://localhost:8001
- **Neo4j Browser**: http://localhost:7475
- **Celery Monitoring**: http://localhost:5555

---

## 📋 Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Neo4j Configuration
NEO4J_PASSWORD=your_secure_password
NEO4J_URI=bolt://localhost:7688
NEO4J_USER=neo4j

# Redis Configuration
REDIS_URL=redis://localhost:6380

# API Configuration
API_V1_STR=/api/v1
PROJECT_NAME=EduNexus

# LLM Configuration (Anthropic)
ANTHROPIC_API_KEY=your_api_key_here

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6380/0
CELERY_RESULT_BACKEND=redis://localhost:6380/0
```

---

## 📁 Project Structure

```
EduNexus_v2/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py         # API endpoints
│   │   ├── core/
│   │   │   ├── config.py         # Configuration
│   │   │   ├── celery_app.py     # Celery setup
│   │   │   └── llm_manager.py    # LLM interactions
│   │   ├── models/
│   │   │   └── schemas.py        # Pydantic schemas
│   │   ├── services/             # Business logic
│   │   └── main.py               # FastAPI app
│   ├── bulk_upload_jobs.py        # Jobs ingestion
│   ├── bulk_upload_syllabus.py    # Syllabus ingestion
│   ├── simulate_market.py         # Market simulator
│   ├── requirements.txt           # Python dependencies
│   └── data_source/
│       ├── dice_jobs.csv          # Job data
│       └── syllabus_pdfs/         # Educational materials
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── GraphVisualizer.jsx
│   │   │   └── SyllabusUploader.jsx
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── data/
│   ├── neo4j_v2/                 # Neo4j database
│   └── redis_v2/                 # Redis data
├── docker-compose.yml
└── README.md
```

---

## 🔑 Key Workflows

### Workflow 1: Job Market Analysis

1. Upload DICE job postings (`bulk_upload_jobs.py`)
2. LLM extracts skills, requirements, and compensation
3. Skills normalized to standard taxonomy
4. Knowledge graph created with relationships
5. Vector embeddings generated for semantic search

### Workflow 2: Curriculum Analysis

1. Upload syllabus PDFs (`bulk_upload_syllabus.py`)
2. PDF parsing extracts course content
3. LLM identifies learning outcomes and skills covered
4. Map educational outcomes to industry skills
5. Identify coverage gaps

### Workflow 3: Gap Detection

1. Run gap analysis (`gap_analyzer.py`)
2. Compare skill demand vs. educational coverage
3. Identify missing skills in curriculum
4. Generate insights and recommendations
5. Export report for stakeholders

### Workflow 4: Market Simulation

1. Start market simulator (`simulate_market.py`)
2. Simulates skill demand evolution
3. Tracks trending skills
4. Updates analytics in real-time
5. Visualize trends on frontend

---

## 📊 API Endpoints

### Core Endpoints

- `GET /api/v1/` - API documentation
- `GET /health` - Health check
- `POST /api/v1/jobs/upload` - Upload job data
- `POST /api/v1/syllabus/upload` - Upload curriculum
- `GET /api/v1/skills/gaps` - Get skill gaps
- `GET /api/v1/graph/visualization` - Get graph data
- `GET /api/v1/analytics/report` - Generate analytics report

---

## 🔄 Celery Tasks

Common Celery tasks:

```python
# Defined in app.services.tasks

analyze_gap_async()              # Run gap analysis
ingest_job_data_async()          # Ingest jobs
ingest_syllabus_async()          # Ingest curriculum
generate_report_async()          # Generate reports
update_embeddings_async()        # Update vector embeddings
```

Monitor tasks via Flower: http://localhost:5555

---

## 🛠️ Development

### Running Tests

```bash
cd backend
pytest tests/
```

### Code Quality

```bash
# Linting
cd frontend
npm run lint

# Format code
cd backend
black .
```

### Database Queries

Access Neo4j:

```bash
# Via browser at http://localhost:7475
# Default: neo4j / password123

# Or via CLI
cypher-shell -u neo4j -p password123
```

---

## 🐛 Troubleshooting

### Neo4j Connection Issues

```bash
# Check if container is running
docker ps | grep neo4j_v2

# View logs
docker logs edunexus_v2_graph

# Restart service
docker-compose restart neo4j_v2
```

### Redis Connection Issues

```bash
# Test Redis connection
redis-cli -p 6380 ping

# View logs
docker logs edunexus_v2_broker
```

### Celery Worker Not Processing Tasks

```bash
# Check if worker is running
# Ensure Redis is accessible
# Restart worker in terminal 2
```

### Frontend Not Loading

```bash
# Clear node_modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

---

## 📝 Configuration

### Backend Configuration

Edit [backend/app/core/config.py](backend/app/core/config.py) for:
- Database connection strings
- API settings
- LLM parameters
- Task scheduling

### Frontend Configuration

Edit [frontend/vite.config.js](frontend/vite.config.js) for:
- Build settings
- Dev server port
- Proxy configuration

---

## 🤝 Contributing

1. Create a feature branch
2. Make changes
3. Test thoroughly
4. Submit a pull request

---

## 📄 License

This project is proprietary. All rights reserved.

---

## 📧 Support

For issues or questions, please refer to the documentation or contact the development team.

---

## 🔗 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Neo4j Documentation](https://neo4j.com/docs/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)

---

**Last Updated**: April 2026  
**Version**: 2.0
