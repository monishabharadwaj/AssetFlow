import { AlertCircle } from "lucide-react";

import { Button } from "../../../shared/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../../../shared/components/ui/card";

type DashboardErrorProps = {
  message?: string;
  onRetry: () => void;
};

export function DashboardError({ message, onRetry }: DashboardErrorProps) {
  return (
    <Card className="border-destructive/50">
      <CardHeader>
        <div className="flex items-center gap-2">
          <AlertCircle className="h-5 w-5 text-destructive" />
          <CardTitle>Unable to load dashboard</CardTitle>
        </div>
        <CardDescription>
          {message ?? "The dashboard summary could not be loaded. Check that the backend is running."}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Button onClick={onRetry} variant="secondary">
          Retry
        </Button>
      </CardContent>
    </Card>
  );
}
