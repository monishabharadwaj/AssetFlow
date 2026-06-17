import { apiDelete, apiGet, apiPatch, apiPost, buildQueryString } from "../../../shared/api/client";
import type {
  Employee,
  EmployeeCreate,
  EmployeeListParams,
  EmployeeUpdate,
  PaginatedResponse,
  Allocation,
} from "../../../shared/api/types";

export function fetchEmployees(params: EmployeeListParams = {}) {
  return apiGet<PaginatedResponse<Employee>>(`/employees${buildQueryString(params)}`);
}

export function fetchEmployee(id: string) {
  return apiGet<Employee>(`/employees/${id}`);
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

export function fetchEmployeeAllocations(employeeId: string, page = 1, pageSize = 20) {
  return apiGet<PaginatedResponse<Allocation>>(
    `/employees/${employeeId}/allocations${buildQueryString({ page, page_size: pageSize })}`,
  );
}
