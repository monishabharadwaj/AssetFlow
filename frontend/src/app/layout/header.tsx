import { useState } from "react";
import { ScanLine, Search } from "lucide-react";

import { AssistantPanel } from "../../features/assistant/components/assistant-panel";
import { QrScannerDialog } from "../../features/assets/components/qr-scanner-dialog";
import { SearchCommand } from "../../shared/components/search-command";
import { Badge } from "../../shared/components/ui/badge";
import { Button } from "../../shared/components/ui/button";
import { Breadcrumbs } from "./breadcrumbs";
import AssistantButton from "../../features/assistant/components/assistant-button";

export function Header() {
  const [scannerOpen, setScannerOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const [assistantOpen, setAssistantOpen] = useState(false);

  return (
    <>
      <header className="border-b border-zinc-800 bg-black shadow-md">
        <div className="flex h-16 items-center justify-between px-4 md:px-6">
          <div className="min-w-0 flex-1">
            <Breadcrumbs />
          </div>
          <div className="flex items-center gap-2">
           <Button
           type="button"
           variant="ghost"
           size="sm"
           onClick={() => setSearchOpen(true)}
           aria-label="Search"
          className="rounded-lg text-zinc-300 transition-all duration-300 hover:bg-amber-400/10 hover:text-amber-100 hover:shadow-[0_0_12px_rgba(251,191,36,0.35)]"
         >
          <Search className="h-4 w-4" />
           </Button>
            <AssistantButton onClick={() => setAssistantOpen(true)} />
            <Button
             type="button"
             size="sm"
             onClick={() => setScannerOpen(true)}
             aria-label="Scan asset QR code"
             className="rounded-lg border border-transparent bg-transparent text-zinc-300 transition-all duration-300 hover:bg-amber-400/10 hover:text-amber-100 hover:border-amber-300/20 hover:shadow-[0_0_12px_rgba(251,191,36,0.35)]"
             >
             <ScanLine className="mr-2 h-4 w-4" />
             <span className="hidden sm:inline">Scan</span>
             </Button>
            <Badge className="border border-amber-300/20 bg-amber-400/10 text-amber-100 shadow-[0_0_10px_rgba(251,191,36,0.25)]">
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
