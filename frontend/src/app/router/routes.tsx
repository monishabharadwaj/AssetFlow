import { Navigate, Route, Routes } from "react-router-dom";

import { AppShell } from "../layout/app-shell";
import { ProtectedRoute } from "./protected-route";
import { RoleRoute } from "./role-route";
import { AssetDetailPage } from "../../pages/asset-detail-page";
import { AssetsPage } from "../../pages/assets-page";
import { DashboardPage } from "../../pages/dashboard-page";
import { DepartmentsPage } from "../../pages/departments-page";
import { EmployeesPage } from "../../pages/employees-page";
import { LoginPage } from "../../pages/login-page";
import { MaintenancePage } from "../../pages/maintenance-page";
import { ReportsPage } from "../../pages/reports-page";

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<AppShell />}>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route element={<RoleRoute />}>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/assets" element={<AssetsPage />} />
            <Route path="/assets/:assetId" element={<AssetDetailPage />} />
            <Route path="/maintenance" element={<MaintenancePage />} />
            <Route path="/departments" element={<DepartmentsPage />} />
            <Route path="/employees" element={<EmployeesPage />} />
            <Route path="/reports" element={<ReportsPage />} />
          </Route>
        </Route>
      </Route>
    </Routes>
  );
}
