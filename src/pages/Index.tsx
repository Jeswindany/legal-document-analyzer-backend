import { useState } from "react";
import { Sidebar } from "@/components/docs/Sidebar";
import { ClassifierDocs } from "@/components/docs/ClassifierDocs";
import { SummarizerDocs } from "@/components/docs/SummarizerDocs";
import { RagChatDocs } from "@/components/docs/RagChatDocs";

export type ApiSection = "classifier" | "summarizer" | "rag-chat";

const Index = () => {
  const [activeSection, setActiveSection] = useState<ApiSection>("classifier");

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar active={activeSection} onNavigate={setActiveSection} />
      <main className="flex-1 overflow-y-auto">
        {activeSection === "classifier" && <ClassifierDocs />}
        {activeSection === "summarizer" && <SummarizerDocs />}
        {activeSection === "rag-chat" && <RagChatDocs />}
      </main>
    </div>
  );
};

export default Index;
