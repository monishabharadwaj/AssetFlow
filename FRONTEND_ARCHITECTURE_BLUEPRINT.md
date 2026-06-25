# AssetFlow AI - Phase 4C Frontend Architecture Blueprint

This document defines the frontend product architecture for AssetFlow AI before React implementation.
It is intentionally code-free and focuses on product structure, UX, scalability, and recruiter-facing quality.

## 1) Backend API Consumption Strategy

The current backend already exposes enough APIs to build a premium V1 UI.

### Screen-to-API mapping

#### Dashboard
- `GET /api/v1/dashboard/summary`
- Drives KPI cards, status chart, department chart, maintenance due count, and recent activity.

#### Assets
- `GET /api/v1/assets`
- `GET /api/v1/assets/search`
- `GET /api/v1/asset-categories`
- `GET /api/v1/asset-types`
- `POST /api/v1/assets`
- `PATCH /api/v1/assets/{asset_id}`
- `DELETE /api/v1/assets/{asset_id}`

#### Asset Detail (showcase page)
- `GET /api/v1/assets/{asset_id}`
- `GET /api/v1/assets/{asset_id}/timeline`
- `GET /api/v1/assets/{asset_id}/allocations`
- `GET /api/v1/assets/{asset_id}/transfers`
- `GET /api/v1/assets/{asset_id}/maintenance`
- `GET /api/v1/assets/{asset_id}/health-history`

#### Asset Lifecycle Actions
- `POST /api/v1/assets/{asset_id}/allocations/assign`
- `POST /api/v1/assets/{asset_id}/allocations/return`
- `POST /api/v1/assets/{asset_id}/allocations/reassign`
- `POST /api/v1/assets/{asset_id}/transfers`
- `POST /api/v1/assets/{asset_id}/maintenance`
- `POST /api/v1/assets/{asset_id}/health-history`

#### Departments
- `POST /api/v1/departments`
- `GET /api/v1/departments`
- `GET /api/v1/departments/{department_id}`
- `PATCH /api/v1/departments/{department_id}`
- `DELETE /api/v1/departments/{department_id}`

#### Employees
- `POST /api/v1/employees`
- `GET /api/v1/employees`
- `GET /api/v1/employees/{employee_id}`
- `PATCH /api/v1/employees/{employee_id}`
- `DELETE /api/v1/employees/{employee_id}`
- `GET /api/v1/employees/{employee_id}/allocations`

## 2) Information Architecture

The product should be asset-centric with operations surfaced in context.

### Route hierarchy

- `/dashboard`
- `/assets`
- `/assets/:assetId`
  - tab: `overview`
  - tab: `timeline`
  - tab: `allocations`
  - tab: `transfers`
  - tab: `maintenance`
  - tab: `health`
- `/maintenance`
- `/departments`
- `/employees`
- `/reports` (Phase 5 shell)
- `/settings` (Phase 5 shell)

### Navigation model

Primary nav:
- Dashboard
- Assets
- Maintenance
- Departments
- Employees
- Reports

Secondary nav:
- Settings
- Help/About

Reasoning:
- Mirrors enterprise operations flow.
- Keeps daily workflows one click away.
- Makes asset detail the core interaction point.

## 3) Application Layout

### Global shell

1. Left sidebar
   - Brand area
   - Primary navigation
   - Collapsible mode
2. Top header
   - Breadcrumbs
   - Global search trigger
   - Notifications area
   - User menu
3. Content canvas
   - Page heading + action toolbar
   - Main content grid

### Why this shell

- Familiar enterprise SaaS pattern (Linear/Stripe/Vercel style).
- Supports deep navigation without context loss.
- Enables keyboard-first navigation and command search in later phases.

## 4) Dashboard Experience Design

Use `GET /api/v1/dashboard/summary` as single source for the dashboard.

### Desktop layout (12-column)

Row 1:
- KPI card: Total Assets
- KPI card: Active Assets
- KPI card: Total Employees
- KPI card: Maintenance Due

Row 2:
- 8 cols: Asset Status Distribution (bar or donut)
- 4 cols: Assets by Department (horizontal bars)

Row 3:
- 8 cols: Recent Activity feed
- 4 cols: Quick Actions panel
  - Register Asset
  - Assign Asset
  - Create Maintenance

### UX details

- KPI cards should allow click-through to filtered list pages.
- Empty dashboard state should include CTA actions and onboarding text.
- Activity feed should include event icon, title, asset id, and timestamp.

## 5) Asset Detail Showcase Page

This is the strongest demo page for recruiters and evaluators.

### Hero section

- Asset name + asset tag
- Status badge
- Type, department, location, assignee chips
- Action buttons:
  - Assign/Reassign
  - Transfer
  - Add Maintenance
  - Add Health Snapshot

### Tab sections

1. Overview
   - Core metadata, warranty, purchase, owner, current state
2. Timeline
   - Unified chronological feed from `/assets/{asset_id}/timeline`
3. Allocations
   - Structured assignment history table
4. Transfers
   - From/to department and location history
5. Maintenance
   - Record list with type/status/cost/date
6. Health
   - Health snapshots and trend chart

### Timeline visual language

- Event icon by type (allocation/transfer/maintenance/health)
- Relative time + precise timestamp tooltip
- Title + compact details card
- Grouping by day with clear separators

## 6) Design System

### Color system

- Base neutral: Slate/Zinc scale
- Primary accent: Indigo/Blue
- Success: Emerald
- Warning: Amber
- Danger: Rose/Red
- Info: Cyan/Sky

### Status semantic colors

- `AVAILABLE` -> emerald
- `ASSIGNED` -> blue
- `IN_MAINTENANCE` -> amber
- `RETIRED` -> zinc
- `DISPOSED` -> rose
- `HIGH_RISK` (future AI state) -> red

### Typography

- Font family: Inter (preferred) or Geist
- Type scale:
  - H1: 28/32 semibold
  - H2: 22/28 semibold
  - Body: 14/20 regular
  - Meta/table: 12/16 medium

### Spacing and surfaces

- 8-point spacing system
- Radius:
  - Cards: 12
  - Inputs/buttons: 8
- Elevation:
  - subtle tiered shadows only
- Borders:
  - low-contrast borders for structured enterprise feel

## 7) Reusable Component Library

### Core components

- `AppShell`
- `PageHeader`
- `KpiCard`
- `MetricChartCard`
- `StatusBadge`
- `EntityDataTable`
- `EntityFiltersBar`
- `TimelineEventItem`
- `ActivityFeed`
- `ActionSheet`
- `FormDialog`
- `ConfirmDialog`
- `SearchCommand`
- `EmptyState`
- `PaginationBar`

### Usage model

- Shared table/filter components across assets, maintenance, employees, departments.
- Timeline components reused in dashboard feed + asset timeline.
- Slide-over action sheets for contextual operations to reduce page transitions.

## 8) Frontend Folder Structure

```text
frontend/
  src/
    app/
      providers/
        query-provider.tsx
        theme-provider.tsx
      router/
        routes.tsx
      layout/
        app-shell.tsx
        sidebar.tsx
        header.tsx
        breadcrumbs.tsx
    features/
      dashboard/
        api/
        hooks/
        components/
        pages/
      assets/
        api/
        hooks/
        components/
        pages/
      maintenance/
      departments/
      employees/
      allocations/
      transfers/
      health/
      timeline/
    shared/
      api/
        client.ts
        query-keys.ts
        types.ts
      components/
        ui/
        data-display/
        feedback/
      hooks/
      lib/
        format.ts
        date.ts
      styles/
        tokens.css
    pages/
      dashboard-page.tsx
      assets-page.tsx
      asset-detail-page.tsx
      maintenance-page.tsx
      departments-page.tsx
      employees-page.tsx
      reports-page.tsx
```

### Why this structure

- Feature-first organization scales with domain complexity.
- Shared API/query primitives enforce consistency.
- Keeps app shell concerns separate from feature logic.

## 9) API Integration Strategy (TanStack Query)

### Query key convention

- `['dashboard','summary']`
- `['assets','list',params]`
- `['assets','search',params]`
- `['assets','detail',assetId]`
- `['assets','timeline',assetId,page,pageSize]`
- `['assets','allocations',assetId,page,pageSize]`
- `['assets','transfers',assetId,page,pageSize]`
- `['assets','maintenance',assetId,page,pageSize]`
- `['assets','health',assetId,page,pageSize]`
- `['departments','list',params]`
- `['employees','list',params]`

### Mutation invalidation rules

Allocation mutations invalidate:
- `assets.detail`
- `assets.timeline`
- `assets.allocations`
- `assets.list/search`
- `dashboard.summary`

Transfer mutation invalidate:
- `assets.detail`
- `assets.timeline`
- `assets.transfers`
- `assets.list/search`
- `dashboard.summary`

Maintenance mutation invalidate:
- `assets.maintenance`
- `assets.detail`
- `assets.timeline`
- `dashboard.summary`

Health snapshot mutation invalidate:
- `assets.health`
- `assets.timeline`

### Data flow policy

- Server remains source of truth.
- Stale-while-revalidate for read pages.
- Optimistic updates only where rollback is simple.
- Centralized error normalization for toast/inline errors.

## 10) Phase 5 Development Roadmap (Implementation Order)

### Phase 5A - App Shell and Foundation (2-3 days)
- Vite + React + TS setup
- Tailwind + shadcn/ui setup
- App shell layout and routing
- Theme tokens and foundational UI primitives

### Phase 5B - Dashboard (3-4 days)
- Integrate `dashboard/summary`
- KPI cards, charts, activity feed
- loading/empty/error states

### Phase 5C - Assets List and Search (4-5 days)
- Data table, filters, pagination
- Create/edit/deactivate flows

### Phase 5D - Asset Detail and Timeline (4-6 days)
- Showcase asset page
- Timeline integration
- Action sheets for assign/transfer/maintenance/health

### Phase 5E - Maintenance Center (2-3 days)
- Maintenance list and detail/update flow

### Phase 5F - Departments and Employees (3-4 days)
- CRUD pages with standardized table/form UX
- Employee allocation history integration

### Phase 5G - UX Polish and Demo Hardening (2-3 days)
- Empty states, micro-interactions, responsive polish
- keyboard shortcuts
- recruiter demo script/readiness

## Review Gate (Before writing React code)

Approve the following before Phase 5 implementation:

1. Information architecture and route hierarchy
2. App shell and navigation model
3. Design tokens and status color semantics
4. Reusable component catalog
5. Query key and invalidation strategy
6. Phase 5 implementation sequence and estimates

Once approved, implementation can proceed with minimal redesign risk.
