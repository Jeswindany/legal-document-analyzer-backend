import { CodeExample } from "./CodeExample";
import { ParamTable } from "./ParamTable";

export function SummarizerDocs() {
  return (
    <div className="max-w-5xl mx-auto px-8 py-12">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        <div>
          <div className="flex items-center gap-3 mb-4">
            <span className="method-badge-post">POST</span>
            <code className="font-mono text-sm text-foreground">/summarize/document</code>
          </div>
          <h2 className="text-2xl font-semibold text-foreground mb-3">Document Summarizer</h2>
          <p className="text-muted-foreground mb-6">
            Generate a concise summary of a legal document, preserving key legal terms and obligations.
          </p>

          <h3 className="text-sm font-semibold text-foreground uppercase tracking-wider mb-3">Request Body</h3>
          <ParamTable
            params={[
              { name: "text", type: "string", required: true, description: "The full legal document text to summarize." },
              { name: "max_length", type: "integer", required: false, default: "300", description: "Maximum length of the generated summary in tokens." },
              { name: "min_length", type: "integer", required: false, default: "50", description: "Minimum length of the generated summary in tokens." },
            ]}
          />

          <h3 className="text-sm font-semibold text-foreground uppercase tracking-wider mt-8 mb-3">Response Fields</h3>
          <ParamTable
            params={[
              { name: "summary", type: "string", required: true, description: "The generated summary of the legal document." },
              { name: "original_length", type: "integer", required: true, description: "Character count of the original document." },
              { name: "summary_length", type: "integer", required: true, description: "Character count of the generated summary." },
              { name: "compression_ratio", type: "float", required: true, description: "Ratio of summary length to original length." },
            ]}
          />
        </div>

        <div className="lg:sticky lg:top-8 lg:self-start">
          <CodeExample
            curl={`curl -X POST http://localhost:8000/summarize/document \\
  -H "Content-Type: application/json" \\
  -d '{
    "text": "This Agreement is entered into as of January 1, 2024, by and between Party A and Party B. The purpose of this agreement is to establish the terms and conditions under which Party A will provide legal consulting services to Party B...",
    "max_length": 150,
    "min_length": 30
  }'`}
            python={`import requests

response = requests.post(
    "http://localhost:8000/summarize/document",
    json={
        "text": "This Agreement is entered into as of "
               "January 1, 2024, by and between Party A "
               "and Party B. The purpose of this agreement "
               "is to establish the terms and conditions...",
        "max_length": 150,
        "min_length": 30
    }
)

print(response.json())`}
            response={`{
  "summary": "Party A agrees to provide legal consulting services to Party B under specified terms. Key provisions include confidentiality obligations, a limitation of liability capped at the total fees paid, and a 30-day termination notice requirement.",
  "original_length": 2847,
  "summary_length": 248,
  "compression_ratio": 0.0871
}`}
          />
        </div>
      </div>
    </div>
  );
}
