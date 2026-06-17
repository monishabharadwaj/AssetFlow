import { apiDelete, apiGet, apiPatch, apiPost, buildQueryString } from "../../../shared/api/client";
import type {
  Department,
  DepartmentCreate,
  DepartmentListParams,
  DepartmentUpdate,
  PaginatedResponse,
} from "../../../shared/api/types";

export function fetchDepartments(params: DepartmentListParams = {}) {
  return apiGet<PaginatedResponse<Department>>(`/departments${buildQueryString(params)}`);
}

export function fetchDepartment(id: string) {
  return apiGet<Department>(`/departments/${id}`);
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
