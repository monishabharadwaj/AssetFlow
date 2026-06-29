import { apiDelete, apiGet, apiPatch, apiPost, buildQueryString } from "@/lib/api";
import type {
  Department,
  DepartmentCreate,
  DepartmentUpdate,
  PaginatedResponse,
} from "@/lib/types/backend";

export function fetchDepartments(params: { page?: number; page_size?: number; is_active?: boolean; search?: string } = {}) {
  return apiGet<PaginatedResponse<Department>>(`/departments${buildQueryString(params)}`);
}

export function createDepartment(data: DepartmentCreate) {
  return apiPost<Department>("/departments", data);
}

export function updateDepartment(id: string, data: DepartmentUpdate) {
  return apiPatch<Department>(`/departments/${id}`, data);
}

export function deactivateDepartment(id: string) {
  return apiDelete<Department>(`/departments/${id}`);
}
