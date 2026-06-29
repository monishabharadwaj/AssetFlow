import { apiGet, apiPatch, apiPost } from "../../shared/api/client";
import type {
  AuthUser,
  ChangePasswordRequest,
  LoginRequest,
  MyWorkspaceResponse,
  PasswordResetResponse,
  TokenResponse,
  UserAdminUpdate,
  UserCreateRequest,
  UserCreateResponse,
} from "./types";

export function loginRequest(body: LoginRequest): Promise<TokenResponse> {
  return apiPost<TokenResponse>("/auth/login", body);
}

export function fetchCurrentUser(): Promise<AuthUser> {
  return apiGet<AuthUser>("/auth/me");
}

export function changePasswordRequest(body: ChangePasswordRequest): Promise<AuthUser> {
  return apiPost<AuthUser>("/auth/change-password", body);
}

export function fetchMyWorkspace(): Promise<MyWorkspaceResponse> {
  return apiGet<MyWorkspaceResponse>("/dashboard/my-workspace");
}

export function listUserAccounts(): Promise<AuthUser[]> {
  return apiGet<AuthUser[]>("/auth/users");
}

export function createUserAccount(body: UserCreateRequest): Promise<UserCreateResponse> {
  return apiPost<UserCreateResponse>("/auth/users", body);
}

export function updateUserAccount(userId: string, body: UserAdminUpdate): Promise<AuthUser> {
  return apiPatch<AuthUser>(`/auth/users/${userId}`, body);
}

export function resetUserPassword(userId: string): Promise<PasswordResetResponse> {
  return apiPost<PasswordResetResponse>(`/auth/users/${userId}/reset-password`, {});
}
