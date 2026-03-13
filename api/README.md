# Legal Document API server

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the server:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Endpoints

| Method | Path                  | Description                        |
| ------ | --------------------- | ---------------------------------- |
| GET    | `/health`             | Health check                       |
| POST   | `/classify/clauses`   | Classify legal clauses             |
| POST   | `/summarize/document` | Summarize a legal document         |
| POST   | `/chat/ingest`        | Ingest documents for RAG retrieval |
| POST   | `/chat/rag`           | Ask questions using RAG            |
