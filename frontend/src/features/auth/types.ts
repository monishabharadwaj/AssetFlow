export type UserRole = "ADMIN" | "MANAGER" | "VIEWER";

export interface AuthUser {
  id: string;
  role: UserRole;
  is_active: boolean;
  must_change_password: boolean;
  created_at: string;
  employee_id: string;
  email: string;
  full_name: string;
  employee_code: string;
  job_title: string | null;
  department_id: string;
  department_name: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  must_change_password: boolean;
}

export interface UserCreateRequest {
  password?: string;
  role: UserRole;
  employee_id?: string;
  first_name?: string;
  last_name?: string;
  email?: string;
  employee_code?: string;
  department_id?: string;
  job_title?: string;
}

export interface UserCreateResponse extends AuthUser {
  temporary_password?: string | null;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

export interface UserAdminUpdate {
  role?: UserRole;
  is_active?: boolean;
}

export interface PasswordResetResponse {
  user: AuthUser;
  temporary_password: string;
}

export interface MyAssetItem {
  id: string;
  asset_tag: string;
  name: string;
  current_status: string;
  asset_type_name: string | null;
}

export interface MyMaintenanceItem {
  asset_id: string;
  asset_tag: string;
  maintenance_type: string;
  scheduled_date: string | null;
  status: string;
  description: string | null;
}

export interface MyNotificationItem {
  id: string;
  title: string;
  severity: string;
  message: string;
  asset_id: string | null;
  created_at: string;
}

export interface MyWorkspaceResponse {
  full_name: string;
  department_name: string;
  role: UserRole;
  assigned_assets: MyAssetItem[];
  upcoming_maintenance: MyMaintenanceItem[];
  notifications: MyNotificationItem[];
  department_asset_count: number;
}

export const PASSWORD_POLICY_HINT =
  "At least 8 characters with uppercase, lowercase, a number, and a special character.";
