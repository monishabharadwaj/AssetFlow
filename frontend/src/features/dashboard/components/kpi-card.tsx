import type { LucideIcon } from "lucide-react";
import { Link } from "react-router-dom";

import { Card, CardContent, CardHeader, CardTitle } from "../../../shared/components/ui/card";
import { cn } from "../../../shared/lib/utils";

type KpiCardProps = {
  title: string;
  value: number;
  subtitle?: string;
  icon?: LucideIcon;
  href?: string;
};

export function KpiCard({ title, value, subtitle, icon: Icon, href }: KpiCardProps) {
  const content = (
    <Card className={cn(href && "transition-shadow hover:shadow-md")}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
        {Icon ? <Icon className="h-4 w-4 text-muted-foreground" /> : null}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-semibold tracking-tight">{value.toLocaleString()}</div>
        {subtitle ? <p className="mt-1 text-xs text-muted-foreground">{subtitle}</p> : null}
      </CardContent>
    </Card>
  );

  if (href) {
    return (
      <Link to={href} className="block">
        {content}
      </Link>
    );
  }

  return content;
}
