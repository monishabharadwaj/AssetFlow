import { ActivityFeed } from "../features/dashboard/components/activity-feed";
import { AnalyticsSection } from "../features/dashboard/components/analytics-section";
import { AttentionQueue } from "../features/dashboard/components/attention-queue";
import { CompactMetricsStrip } from "../features/dashboard/components/compact-metrics-strip";
import { DashboardError } from "../features/dashboard/components/dashboard-error";
import { DashboardSkeleton } from "../features/dashboard/components/dashboard-skeleton";
import { MyWorkspacePanel } from "../features/dashboard/components/my-workspace-panel";
import { NotificationsPanel } from "../features/operations/components/notifications-panel";
import { PipelineStatusStrip } from "../features/operations/components/pipeline-status-strip";
import { AiRecommendationsPanel } from "../features/intelligence/components/ai-recommendations-panel";
import { QuickActionsPanel } from "../features/dashboard/components/quick-actions-panel";
import { useAuth } from "../features/auth/auth-context";
import { usePermissions } from "../features/auth/use-permissions";
import { useDashboardSummary } from "../features/dashboard/hooks/use-dashboard-summary";

export function DashboardPage() {
  const { user } = useAuth();
  const { can } = usePermissions();
  const { data, isLoading, isError, error, refetch } = useDashboardSummary();

  if (isLoading) {
    return <DashboardSkeleton />;
  }

  if (isError || !data) {
    return (
      <div className="grid gap-4 md:gap-6">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">Operations Center</h2>
          <p className="text-sm text-muted-foreground">Live asset operations and attention queue</p>
        </div>
        <DashboardError
          message={error instanceof Error ? error.message : undefined}
          onRetry={() => void refetch()}
        />
      </div>
    );
  }

  return (
    <div className="grid gap-4 md:gap-6">
      <div>
        <h2 className="text-2xl font-semibold tracking-tight">Operations Center</h2>
        <p className="text-sm text-muted-foreground">
          {user?.role === "ADMIN"
            ? "Organization-wide operations and attention queue"
            : `${user?.department_name ?? "Department"} operations and your assigned assets`}
        </p>
      </div>

      <MyWorkspacePanel />

      <CompactMetricsStrip summary={data} />

      <div className="grid gap-4 lg:grid-cols-12">
        <div className="lg:col-span-4">
          <AttentionQueue items={data.attention_items} />
        </div>
        <div className="lg:col-span-8">
          <ActivityFeed activities={data.recent_activity} />
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-12">
        <div className="lg:col-span-12">
          <AiRecommendationsPanel />
        </div>
      </div>

      {can("intelligence:run") ? <PipelineStatusStrip /> : null}

      {can("assets:write") ? (
        <div className="grid gap-4 lg:grid-cols-12">
          <div className="lg:col-span-6">
            <NotificationsPanel />
          </div>
          <div className="lg:col-span-6">
            <QuickActionsPanel />
          </div>
        </div>
      ) : (
        <NotificationsPanel />
      )}

      <div className="grid gap-4 lg:grid-cols-12">
        <div className="lg:col-span-8">
          <AnalyticsSection
            assetsByStatus={data.assets_by_status}
            assetsByDepartment={data.assets_by_department}
          />
        </div>
      </div>
    </div>
  );
}
