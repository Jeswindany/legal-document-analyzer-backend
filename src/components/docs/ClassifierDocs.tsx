import { CodeExample } from "./CodeExample";
import { ParamTable } from "./ParamTable";

export function ClassifierDocs() {
  return (
    <div className="max-w-5xl mx-auto px-8 py-12">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        {/* Left: Documentation */}
        <div>
          <div className="flex items-center gap-3 mb-4">
            <span className="method-badge-post">POST</span>
            <code className="font-mono text-sm text-foreground">/classify/clauses</code>
          </div>
          <h2 className="text-2xl font-semibold text-foreground mb-3">Clause Classifier</h2>
          <p className="text-muted-foreground mb-6">
            Classify legal clauses in a document. Splits the text into paragraphs, classifies each one, 
            and returns clauses that exceed the confidence threshold.
          </p>

          <h3 className="text-sm font-semibold text-foreground uppercase tracking-wider mb-3">Request Body</h3>
          <ParamTable
            params={[
              {
                name: "text",
                type: "string",
                required: true,
                description: "Full legal document or clause text to classify.",
              },
              {
                name: "file",
                type: "file",
                required: true,
                description: "PDF or DOCX file containing the legal document to classify.",
              },
              {
                name: "threshold",
                type: "float",
                required: false,
                default: "0.5",
                description: "Minimum confidence score to include a clause (0.0–1.0).",
              },
            ]}
          />

          <h3 className="text-sm font-semibold text-foreground uppercase tracking-wider mt-8 mb-3">Response Fields</h3>
          <ParamTable
            params={[
              {
                name: "clauses",
                type: "array[ClassifiedClause]",
                required: true,
                description: "Array of classified clauses with type, confidence, and text.",
              },
              {
                name: "total_clauses_found",
                type: "integer",
                required: true,
                description: "Total number of clauses that exceeded the threshold.",
              },
            ]}
          />

          <h3 className="text-sm font-semibold text-foreground uppercase tracking-wider mt-8 mb-3">Clause Types</h3>
          <div className="flex flex-wrap gap-2">
            {[
              "indemnification", "limitation_of_liability", "termination",
              "confidentiality", "governing_law", "force_majeure",
              "arbitration", "non_compete", "intellectual_property", "other",
            ].map((label) => (
              <span key={label} className="px-2 py-1 bg-accent text-accent-foreground text-xs font-mono rounded">
                {label}
              </span>
            ))}
          </div>
        </div>

        {/* Right: Code Examples */}
        <div className="lg:sticky lg:top-8 lg:self-start">
          <CodeExample
            curl={`curl -X POST http://localhost:8000/classify/clauses \\
  -H "Content-Type: application/json" \\
  -d '{
    "text": "The Receiving Party shall not disclose any Confidential Information to third parties without prior written consent. In the event of a breach, the Disclosing Party may terminate this agreement with 30 days written notice.",
    "file": "document.pdf",  # Optional: include a file instead of text
    "threshold": 0.5
  }'`}
            python={`import requests

response = requests.post(
    "http://localhost:8000/classify/clauses",
    json={
        "text": "The Receiving Party shall not disclose "
               "any Confidential Information to third "
               "parties without prior written consent. "
               "In the event of a breach, the Disclosing "
               "Party may terminate this agreement with "
               "30 days written notice.",
        "file": open("document.pdf", "rb"),  # Optional: include a file instead of text
        "threshold": 0.5
    }
)

print(response.json())`}
            response={`{
 "groups": {
   "termination_employment": [],
   "confidentiality_ip": [],
   "liability_indemnity_remedies": [],
   "governance_compliance_dispute": [],
   "finance_transactions_corporate": [],
   "other": []
 },
 "total_clauses_found": 0
} `}
          />
        </div>
      </div>
    </div>
  );
}
