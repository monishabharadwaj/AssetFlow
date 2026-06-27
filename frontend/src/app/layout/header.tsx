import { useState } from "react";
import { Bot, ScanLine, Search } from "lucide-react";

import { AssistantPanel } from "../../features/assistant/components/assistant-panel";
import { QrScannerDialog } from "../../features/assets/components/qr-scanner-dialog";
import { SearchCommand } from "../../shared/components/search-command";
import { Badge } from "../../shared/components/ui/badge";
import { Button } from "../../shared/components/ui/button";
import { Breadcrumbs } from "./breadcrumbs";

export function Header() {
  const [scannerOpen, setScannerOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const [assistantOpen, setAssistantOpen] = useState(false);

  return (
    <>
      <header className="border-b bg-card">
        <div className="flex h-16 items-center justify-between px-4 md:px-6">
          <div className="min-w-0 flex-1">
            <Breadcrumbs />
          </div>
          <div className="flex items-center gap-2">
            <Button
  type="button"
  variant="ghost"
  size="icon"
  onClick={() => setSearchOpen(true)}
  aria-label="Search"
  className="rounded-xl border border-slate-700 bg-slate-800/70 text-slate-300 shadow-[0_0_10px_rgba(59,130,246,0.15)] transition-all duration-300 hover:border-blue-500/60 hover:bg-slate-700 hover:text-white hover:shadow-[0_0_20px_rgba(59,130,246,0.45)]"
>
  <Search className="h-5 w-5" />
</Button>
            <Button
             type="button"
             size="sm"
             onClick={() => setAssistantOpen(true)}
             aria-label="Open AI assistant"
             className="rounded-xl border border-blue-500/40 bg-blue-600 px-4 text-white shadow-[0_0_18px_rgba(59,130,246,0.35)] transition-all duration-300 hover:bg-blue-500 hover:shadow-[0_0_22px_rgba(59,130,246,0.55)]"
             >
             <Bot className="mr-2 h-4 w-4" />
             <span className="hidden sm:inline">AI Assistant</span>
             </Button>
            <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={() => setScannerOpen(true)}
            aria-label="Scan asset QR code"
            className="rounded-xl border border-slate-700 bg-slate-800/70 text-slate-300 shadow-[0_0_10px_rgba(59,130,246,0.15)] transition-all duration-300 hover:border-blue-500/60 hover:bg-slate-700 hover:text-white hover:shadow-[0_0_20px_rgba(59,130,246,0.45)]"
           >
           <ScanLine className="mr-2 h-4 w-4" />
           <span className="hidden sm:inline">Scan</span>
           </Button>
            <Badge className="cursor-default rounded-xl border border-slate-700 bg-slate-800 px-3 py-1 text-slate-200 shadow-[0_0_10px_rgba(59,130,246,0.15)] transition-all duration-300 hover:border-blue-500/60 hover:shadow-[0_0_20px_rgba(59,130,246,0.45)]">
  Demo User
</Badge>
          </div>
        </div>
      </header>
      <QrScannerDialog open={scannerOpen} onOpenChange={setScannerOpen} />
      <SearchCommand open={searchOpen} onOpenChange={setSearchOpen} />
      <AssistantPanel open={assistantOpen} onOpenChange={setAssistantOpen} />
    </>
  );
}
