import { Bell, Search } from "lucide-react";

import { Badge } from "../../shared/components/ui/badge";
import { Button } from "../../shared/components/ui/button";
import { Breadcrumbs } from "./breadcrumbs";

export function Header() {
  return (
    <header className="border-b bg-card">
      <div className="flex h-16 items-center justify-between px-4 md:px-6">
        <div className="min-w-0 flex-1">
          <Breadcrumbs />
        </div>
        <div className="flex items-center gap-2">
          <Button variant="secondary" size="sm" className="hidden sm:inline-flex">
            <Search className="mr-2 h-4 w-4" />
            Search
          </Button>
          <Button variant="ghost" size="icon" aria-label="Notifications">
            <Bell className="h-4 w-4" />
          </Button>
          <Badge variant="secondary">Demo User</Badge>
        </div>
      </div>
    </header>
  );
}
