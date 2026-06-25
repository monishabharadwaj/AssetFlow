import { Card, CardContent, CardHeader } from "../../../shared/components/ui/card";

function SkeletonBlock({ className }: { className?: string }) {
  return <div className={`animate-pulse rounded-md bg-muted ${className ?? ""}`} />;
}

export function DashboardSkeleton() {
  return (
    <div className="grid gap-4 md:gap-6">
      <div>
        <SkeletonBlock className="h-8 w-48" />
        <SkeletonBlock className="mt-2 h-4 w-72" />
      </div>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <SkeletonBlock key={index} className="h-16 w-full" />
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-12">
        <Card className="lg:col-span-4">
          <CardHeader>
            <SkeletonBlock className="h-5 w-36" />
          </CardHeader>
          <CardContent className="space-y-2">
            {Array.from({ length: 4 }).map((_, index) => (
              <SkeletonBlock key={index} className="h-14 w-full" />
            ))}
          </CardContent>
        </Card>
        <Card className="lg:col-span-8">
          <CardHeader>
            <SkeletonBlock className="h-5 w-32" />
          </CardHeader>
          <CardContent className="space-y-2">
            {Array.from({ length: 5 }).map((_, index) => (
              <SkeletonBlock key={index} className="h-16 w-full" />
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
