export type PaginatedResponse<T> = {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
};

export type AssetStatus =
  | "AVAILABLE"
  | "ASSIGNED"
  | "IN_MAINTENANCE"
  | "RETIRED"
  | "DISPOSED";

export type MaintenanceType =
  | "PREVENTIVE"
  | "CORRECTIVE"
  | "INSPECTION"
  | "UPGRADE"
  | "OTHER";

export type MaintenanceStatus =
  | "SCHEDULED"
  | "IN_PROGRESS"
  | "COMPLETED"
  | "CANCELLED";

export type AllocationAction = "ASSIGN" | "RETURN" | "REASSIGN";

export type DashboardSummary = {
  total_assets: number;
  total_active_assets: number;
  total_employees: number;
  total_active_employees: number;
  total_departments: number;
  total_active_departments: number;
  assets_by_status: Array<{ status: string; count: number }>;
  assets_by_department: Array<{
    department_id: string;
    department_name: string;
    count: number;
  }>;
  maintenance_due_count: number;
  recent_activity: Array<{
    activity_type: string;
    occurred_at: string;
    asset_id: string;
    message: string;
  }>;
};

export type Asset = {
  id: string;
  asset_tag: string;
  name: string;
  asset_type_id: string;
  purchase_date: string;
  purchase_cost: string;
  current_status: AssetStatus;
  current_location: string;
  current_department_id: string;
  current_assigned_employee_id: string | null;
  serial_number: string | null;
  manufacturer: string | null;
  model: string | null;
  warranty_expiry: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type AssetCreate = {
  asset_tag: string;
  name: string;
  asset_type_id: string;
  purchase_date: string;
  purchase_cost: number;
  current_location?: string;
  current_department_id: string;
  serial_number?: string | null;
  manufacturer?: string | null;
  model?: string | null;
  warranty_expiry?: string | null;
};

export type AssetUpdate = Partial<{
  asset_tag: string;
  name: string;
  asset_type_id: string;
  purchase_date: string;
  purchase_cost: number;
  current_status: AssetStatus;
  current_location: string;
  current_department_id: string;
  serial_number: string | null;
  manufacturer: string | null;
  model: string | null;
  warranty_expiry: string | null;
  is_active: boolean;
}>;

export type AssetListParams = {
  page?: number;
  page_size?: number;
  is_active?: boolean;
};

export type AssetSearchParams = {
  page?: number;
  page_size?: number;
  name?: string;
  asset_tag?: string;
  serial_number?: string;
  current_status?: AssetStatus;
  current_department_id?: string;
  current_location?: string;
};

export type AssetCategory = {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
};

export type AssetType = {
  id: string;
  category_id: string;
  name: string;
  description: string | null;
  created_at: string;
  updated_at: string;
};

export type Department = {
  id: string;
  name: string;
  code: string;
  description: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type DepartmentCreate = {
  name: string;
  code: string;
  description?: string | null;
};

export type DepartmentUpdate = Partial<DepartmentCreate & { is_active: boolean }>;

export type DepartmentListParams = {
  page?: number;
  page_size?: number;
  is_active?: boolean;
  search?: string;
};

export type Employee = {
  id: string;
  department_id: string;
  employee_code: string;
  first_name: string;
  last_name: string;
  email: string;
  job_title: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type EmployeeCreate = {
  department_id: string;
  employee_code: string;
  first_name: string;
  last_name: string;
  email: string;
  job_title?: string | null;
};

export type EmployeeUpdate = Partial<EmployeeCreate & { is_active: boolean }>;

export type EmployeeListParams = {
  page?: number;
  page_size?: number;
  department_id?: string;
  is_active?: boolean;
  search?: string;
};

export type Allocation = {
  id: string;
  asset_id: string;
  employee_id: string;
  action: AllocationAction;
  allocated_at: string;
  returned_at: string | null;
  notes: string | null;
  performed_by: string | null;
  created_at: string;
};

export type AllocationAssignRequest = {
  employee_id: string;
  allocated_at: string;
  notes?: string | null;
};

export type AllocationReturnRequest = {
  returned_at: string;
  notes?: string | null;
};

export type AllocationReassignRequest = {
  employee_id: string;
  allocated_at: string;
  notes?: string | null;
};

export type Transfer = {
  id: string;
  asset_id: string;
  from_department_id: string;
  to_department_id: string;
  from_location: string;
  to_location: string;
  transferred_at: string;
  reason: string | null;
  performed_by: string | null;
  created_at: string;
};

export type TransferCreate = {
  to_department_id: string;
  to_location: string;
  transferred_at: string;
  reason?: string | null;
};

export type Maintenance = {
  id: string;
  asset_id: string;
  maintenance_type: MaintenanceType;
  status: MaintenanceStatus;
  scheduled_date: string | null;
  completed_date: string | null;
  cost: string | null;
  description: string;
  service_provider: string | null;
  performed_by: string | null;
  created_at: string;
  updated_at: string;
};

export type MaintenanceCreate = {
  maintenance_type: MaintenanceType;
  status?: MaintenanceStatus;
  scheduled_date?: string | null;
  completed_date?: string | null;
  cost?: number | null;
  description: string;
  service_provider?: string | null;
};

export type MaintenanceUpdate = Partial<MaintenanceCreate>;

export type HealthHistory = {
  id: string;
  asset_id: string;
  recorded_at: string;
  health_score: string | null;
  condition_rating: number | null;
  operational_hours: string | null;
  failure_count: number;
  days_since_last_maintenance: number | null;
  age_in_days: number | null;
  depreciation_ratio: string | null;
  notes: string | null;
  created_at: string;
};

export type HealthHistoryCreate = {
  recorded_at?: string | null;
  health_score?: number | null;
  condition_rating?: number | null;
  operational_hours?: number | null;
  failure_count?: number;
  notes?: string | null;
};

export type TimelineEvent = {
  event_type: string;
  occurred_at: string;
  title: string;
  details: Record<string, unknown>;
};

export type AssetTimelineResponse = {
  asset_id: string;
  items: TimelineEvent[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
};
