import { useState } from "react";
import { Bot, LogOut, ScanLine, Search } from "lucide-react";

import { AssistantPanel } from "../../features/assistant/components/assistant-panel";
import { useAuth } from "../../features/auth/auth-context";
import { QrScannerDialog } from "../../features/assets/components/qr-scanner-dialog";
import { SearchCommand } from "../../shared/components/search-command";
import { Badge } from "../../shared/components/ui/badge";
import { Button } from "../../shared/components/ui/button";
import { Breadcrumbs } from "./breadcrumbs";

export function Header() {
  const { user, logout } = useAuth();
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
          <div className="flex shrink-0 items-center gap-2">
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
              Assistant
            </Button>
            <Button
              type="button"
              variant="secondary"
              size="sm"
              onClick={() => setScannerOpen(true)}
              aria-label="Scan asset QR code"
            >
              <ScanLine className="mr-2 h-4 w-4" />
              Scan
            </Button>
            <Badge variant="secondary" title={user?.email ?? undefined}>
              {user?.full_name ?? "User"} · {user?.role ?? "—"}
              {user?.department_name ? ` · ${user.department_name}` : ""}
            </Badge>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={logout}
              aria-label="Sign out"
            >
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </header>
      <QrScannerDialog open={scannerOpen} onOpenChange={setScannerOpen} />
      <SearchCommand open={searchOpen} onOpenChange={setSearchOpen} />
      <AssistantPanel open={assistantOpen} onOpenChange={setAssistantOpen} />
    </>
  );
}
