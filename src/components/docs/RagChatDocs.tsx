import { CodeExample } from "./CodeExample";
import { ParamTable } from "./ParamTable";

export function RagChatDocs() {
  return (
    <div className="max-w-5xl mx-auto px-8 py-12 space-y-16">
      {/* Ingest Endpoint */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        <div>
          <div className="flex items-center gap-3 mb-4">
            <span className="method-badge-post">POST</span>
            <code className="font-mono text-sm text-foreground">/chat/ingest</code>
          </div>
          <h2 className="text-2xl font-semibold text-foreground mb-3">Ingest Documents</h2>
          <p className="text-muted-foreground mb-6">
            Ingest and index legal documents for RAG retrieval. Splits documents into chunks, generates embeddings, and adds them to the FAISS vector index.
          </p>

          <h3 className="text-sm font-semibold text-foreground uppercase tracking-wider mb-3">Request Body</h3>
          <ParamTable
            params={[
              { name: "documents", type: "array[string]", required: true, description: "List of document text chunks to index for retrieval." },
              { name: "chunk_size", type: "integer", required: false, default: "500", description: "Target size (in characters) for splitting documents into chunks." },
            ]}
          />

          <h3 className="text-sm font-semibold text-foreground uppercase tracking-wider mt-8 mb-3">Response Fields</h3>
          <ParamTable
            params={[
              { name: "chunks_indexed", type: "integer", required: true, description: "Number of chunks added to the index." },
              { name: "total_chunks", type: "integer", required: true, description: "Total chunks currently in the index." },
            ]}
          />
        </div>

        <div className="lg:sticky lg:top-8 lg:self-start">
          <CodeExample
            curl={`curl -X POST http://localhost:8000/chat/ingest \\
  -H "Content-Type: application/json" \\
  -d '{
    "documents": [
      "This Non-Disclosure Agreement governs the exchange of confidential information between the parties...",
      "The Software License Agreement grants the licensee a non-exclusive, non-transferable right to use..."
    ],
    "chunk_size": 500
  }'`}
            python={`import requests

response = requests.post(
    "http://localhost:8000/chat/ingest",
    json={
        "documents": [
            "This Non-Disclosure Agreement governs "
            "the exchange of confidential information "
            "between the parties...",
            "The Software License Agreement grants "
            "the licensee a non-exclusive right..."
        ],
        "chunk_size": 500
    }
)

print(response.json())`}
            response={`{
  "chunks_indexed": 12,
  "total_chunks": 12
}`}
          />
        </div>
      </div>

      <hr className="border-border" />

      {/* RAG Chat Endpoint */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        <div>
          <div className="flex items-center gap-3 mb-4">
            <span className="method-badge-post">POST</span>
            <code className="font-mono text-sm text-foreground">/chat/rag</code>
          </div>
          <h2 className="text-2xl font-semibold text-foreground mb-3">RAG Chat</h2>
          <p className="text-muted-foreground mb-6">
            Ask a legal question using Retrieval-Augmented Generation. Retrieves relevant document chunks from the index, then generates an answer grounded in the retrieved context.
          </p>

          <h3 className="text-sm font-semibold text-foreground uppercase tracking-wider mb-3">Request Body</h3>
          <ParamTable
            params={[
              { name: "query", type: "string", required: true, description: "The legal question to answer." },
              { name: "top_k", type: "integer", required: false, default: "3", description: "Number of relevant document chunks to retrieve." },
              { name: "max_tokens", type: "integer", required: false, default: "512", description: "Maximum tokens in the generated response." },
            ]}
          />

          <h3 className="text-sm font-semibold text-foreground uppercase tracking-wider mt-8 mb-3">Response Fields</h3>
          <ParamTable
            params={[
              { name: "answer", type: "string", required: true, description: "The AI-generated answer based on retrieved context." },
              { name: "sources", type: "array[RetrievedChunk]", required: true, description: "Document chunks used as context, with relevance scores." },
            ]}
          />
        </div>

        <div className="lg:sticky lg:top-8 lg:self-start">
          <CodeExample
            curl={`curl -X POST http://localhost:8000/chat/rag \\
  -H "Content-Type: application/json" \\
  -d '{
    "query": "What are the confidentiality obligations in the NDA?",
    "top_k": 3,
    "max_tokens": 256
  }'`}
            python={`import requests

response = requests.post(
    "http://localhost:8000/chat/rag",
    json={
        "query": "What are the confidentiality "
                 "obligations in the NDA?",
        "top_k": 3,
        "max_tokens": 256
    }
)

print(response.json())`}
            response={`{
  "answer": "Based on the NDA, the receiving party must: (1) maintain strict confidentiality of all disclosed information, (2) limit access to authorized personnel only, (3) not use confidential information for any purpose other than the agreed business relationship, and (4) return or destroy all materials upon termination.",
  "sources": [
    {
      "text": "The Receiving Party shall hold and maintain the Confidential Information in strict confidence...",
      "relevance_score": 0.9241
    },
    {
      "text": "Upon termination of this Agreement, all confidential materials shall be returned...",
      "relevance_score": 0.8103
    }
  ]
}`}
          />
        </div>
      </div>
    </div>
  );
}
