# Space Biology Knowledge Engine - Backend

This is the backend service for the Space Biology Knowledge Engine, a NASA bioscience publication knowledge graph system.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables in `.env` file:
```
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
OPENAI_API_KEY=your_openai_api_key
```

3. Start Neo4j database (Docker example):
```bash
docker run --name neo4j -p 7474:7474 -p 7687:7687 -e NEO4J_AUTH=neo4j/password -d neo4j:latest
```

4. Seed the database with sample data:
```bash
python app/seed_data.py
```

5. Run the server:
```bash
uvicorn app.main:app --reload
```

6. Visit API documentation:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

- `GET /graph` - Get knowledge graph data
- `GET /graph/node/{id}` - Get detailed node information
- `POST /summarize` - Generate AI summary of publication text
- `GET /search?query=xxx` - Search publications by keywords
- `POST /compare` - Compare two publications

## Technology Stack
- FastAPI (Python)
- Neo4j (Graph Database)
- OpenAI API (Text summarization)