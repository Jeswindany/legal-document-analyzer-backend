# Legal Document API server

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Run api/scripts/download_model.py from root folder to download the model required

Run the server:

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

## Endpoints

| Method | Path                  | Description                        |
| ------ | --------------------- | ---------------------------------- |
| GET    | `/health`             | Health check                       |
| POST   | `/classify/clauses`   | Classify legal clauses             |
| POST   | `/summarize/document` | Summarize a legal document         |
| POST   | `/chat/ingest`        | Ingest documents for RAG retrieval |
| POST   | `/chat/rag`           | Ask questions using RAG            |
