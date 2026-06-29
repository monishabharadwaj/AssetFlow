import { apiDelete, apiGet, apiPatch, apiPost, buildQueryString } from "@/lib/api";
import type {
  Employee,
  EmployeeCreate,
  EmployeeUpdate,
  PaginatedResponse,
} from "@/lib/types/backend";

export function fetchEmployees(params: { page?: number; page_size?: number; search?: string; department_id?: string; is_active?: boolean } = {}) {
  return apiGet<PaginatedResponse<Employee>>(`/employees${buildQueryString(params)}`);
}

export function createEmployee(data: EmployeeCreate) {
  return apiPost<Employee>("/employees", data);
}

export function updateEmployee(id: string, data: EmployeeUpdate) {
  return apiPatch<Employee>(`/employees/${id}`, data);
}

export function deactivateEmployee(id: string) {
  return apiDelete<Employee>(`/employees/${id}`);
}
