interface CodeExampleProps {
  curl: string;
  python: string;
  response: string;
}

import { useState } from "react";

export function CodeExample({ curl, python, response }: CodeExampleProps) {
  const [tab, setTab] = useState<"curl" | "python">("curl");

  return (
    <div className="space-y-4">
      <div>
        <div className="flex gap-1 mb-2">
          {(["curl", "python"] as const).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`px-3 py-1 rounded text-xs font-mono font-medium transition-colors ${
                tab === t
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {t === "curl" ? "cURL" : "Python"}
            </button>
          ))}
        </div>
        <pre className="code-block">
          <code>{tab === "curl" ? curl : python}</code>
        </pre>
      </div>
      <div>
        <p className="text-xs font-medium text-muted-foreground mb-2 uppercase tracking-wider">Response</p>
        <pre className="code-block">
          <code>{response}</code>
        </pre>
      </div>
    </div>
  );
}
