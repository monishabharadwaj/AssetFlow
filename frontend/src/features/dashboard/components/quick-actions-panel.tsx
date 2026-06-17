import { Box, UserPlus, Wrench } from "lucide-react";
import { Link } from "react-router-dom";

import { buttonVariants } from "../../../shared/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../../shared/components/ui/card";
import { cn } from "../../../shared/lib/utils";

export function QuickActionsPanel() {
  const linkClass = cn(buttonVariants({ variant: "secondary" }), "w-full justify-start");

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Quick Actions</CardTitle>
        <CardDescription>Common lifecycle operations</CardDescription>
      </CardHeader>
      <CardContent className="space-y-2">
        <Link to="/assets?create=true" className={linkClass}>
          <Box className="mr-2 h-4 w-4" />
          Register Asset
        </Link>
        <Link to="/assets" className={linkClass}>
          <UserPlus className="mr-2 h-4 w-4" />
          Assign Asset
        </Link>
        <Link to="/maintenance" className={linkClass}>
          <Wrench className="mr-2 h-4 w-4" />
          Create Maintenance
        </Link>
      </CardContent>
    </Card>
  );
}
