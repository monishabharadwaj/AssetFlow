import { apiGet, apiPost } from "@/lib/api";
import type { AuthUser, ChangePasswordRequest, LoginRequest, TokenResponse } from "@/lib/types/backend";
import type { User } from "@/lib/types/ui";

export function loginRequest(body: LoginRequest): Promise<TokenResponse> {
  return apiPost<TokenResponse>("/auth/login", body);
}

export function fetchCurrentUser(): Promise<AuthUser> {
  return apiGet<AuthUser>("/auth/me");
}

export function changePasswordRequest(body: ChangePasswordRequest): Promise<AuthUser> {
  return apiPost<AuthUser>("/auth/change-password", body);
}

export function mapAuthUser(user: AuthUser): User {
  return {
    id: user.id,
    email: user.email,
    full_name: user.full_name,
    role: user.role,
    department_id: user.department_id,
    department_name: user.department_name,
    must_change_password: user.must_change_password,
    job_title: user.job_title,
    employee_code: user.employee_code,
  };
}
