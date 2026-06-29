export type UserRole = "ADMIN" | "MANAGER" | "VIEWER";

export interface AuthUser {
  id: string;
  role: UserRole;
  is_active: boolean;
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
}

export interface UserCreateRequest {
  password: string;
  role: UserRole;
  employee_id?: string;
  first_name?: string;
  last_name?: string;
  email?: string;
  employee_code?: string;
  department_id?: string;
  job_title?: string;
}
