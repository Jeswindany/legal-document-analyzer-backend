import type { ApiSection } from "@/pages/Index";
import { FileText, MessageSquare, Tag } from "lucide-react";

interface SidebarProps {
  active: ApiSection;
  onNavigate: (section: ApiSection) => void;
}

const NAV_ITEMS: { id: ApiSection; label: string; icon: React.ElementType }[] = [
  { id: "classifier", label: "Clause Classifier", icon: Tag },
  { id: "summarizer", label: "Document Summarizer", icon: FileText },
  { id: "rag-chat", label: "RAG Chat", icon: MessageSquare },
];

export function Sidebar({ active, onNavigate }: SidebarProps) {
  return (
    <aside className="w-64 border-r border-border bg-background flex-shrink-0 sticky top-0 h-screen overflow-y-auto">
      <div className="p-6">
        <h1 className="text-lg font-semibold text-foreground tracking-tight">Legal AI API</h1>
        <p className="text-xs text-muted-foreground mt-1">v1.0.0</p>
      </div>

      <nav className="px-3 pb-6">
        <p className="px-3 mb-2 text-xs font-medium text-muted-foreground uppercase tracking-wider">
          Endpoints
        </p>
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={active === item.id ? "sidebar-link-active w-full text-left flex items-center gap-2" : "sidebar-link w-full text-left flex items-center gap-2"}
            >
              <Icon className="w-4 h-4 flex-shrink-0" />
              {item.label}
            </button>
          );
        })}
      </nav>

      <div className="px-6 py-4 border-t border-border">
        <p className="text-xs text-muted-foreground">Base URL</p>
        <code className="text-xs font-mono text-foreground mt-1 block">
          http://localhost:8000
        </code>
      </div>
    </aside>
  );
}
