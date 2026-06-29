import { apiGet, apiPost } from "../../shared/api/client";
import type { AuthUser, LoginRequest, TokenResponse, UserCreateRequest } from "./types";

export function loginRequest(body: LoginRequest): Promise<TokenResponse> {
  return apiPost<TokenResponse>("/auth/login", body);
}

export function fetchCurrentUser(): Promise<AuthUser> {
  return apiGet<AuthUser>("/auth/me");
}

export function listUserAccounts(): Promise<AuthUser[]> {
  return apiGet<AuthUser[]>("/auth/users");
}

export function createUserAccount(body: UserCreateRequest): Promise<AuthUser> {
  return apiPost<AuthUser>("/auth/users", body);
}