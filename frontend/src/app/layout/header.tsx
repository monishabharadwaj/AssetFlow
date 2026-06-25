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
              size="sm"
              onClick={() => setSearchOpen(true)}
              aria-label="Search"
            >
              <Search className="h-4 w-4" />
            </Button>
            <Button
              type="button"
              variant="secondary"
              size="sm"
              onClick={() => setAssistantOpen(true)}
              aria-label="Open AI assistant"
            >
              <Bot className="mr-2 h-4 w-4" />
              <span className="hidden sm:inline">Assistant</span>
            </Button>
            <Button
              type="button"
              variant="secondary"
              size="sm"
              onClick={() => setScannerOpen(true)}
              aria-label="Scan asset QR code"
            >
              <ScanLine className="mr-2 h-4 w-4" />
              <span className="hidden sm:inline">Scan</span>
            </Button>
            <Badge variant="secondary">Demo User</Badge>
          </div>
        </div>
      </header>
      <QrScannerDialog open={scannerOpen} onOpenChange={setScannerOpen} />
      <SearchCommand open={searchOpen} onOpenChange={setSearchOpen} />
      <AssistantPanel open={assistantOpen} onOpenChange={setAssistantOpen} />
    </>
  );
}
