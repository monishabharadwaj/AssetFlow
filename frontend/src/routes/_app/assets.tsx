import { createFileRoute, Outlet } from "@tanstack/react-router";

import { guardRoute } from "@/lib/route-guards";

export const Route = createFileRoute("/_app/assets")({
  beforeLoad: () => guardRoute("/assets"),
  component: AssetsLayout,
});

function AssetsLayout() {
  return <Outlet />;
}
