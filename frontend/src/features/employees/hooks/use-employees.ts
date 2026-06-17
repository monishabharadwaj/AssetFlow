import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { queryKeys } from "../../../shared/api/query-keys";
import type { EmployeeCreate, EmployeeListParams, EmployeeUpdate } from "../../../shared/api/types";
import {
  createEmployee,
  deactivateEmployee,
  fetchEmployee,
  fetchEmployeeAllocations,
  fetchEmployees,
  updateEmployee,
} from "../api/employees-api";

export function useEmployeesList(params: EmployeeListParams = { page: 1, page_size: 20 }) {
  return useQuery({
    queryKey: queryKeys.employees.list(params),
    queryFn: () => fetchEmployees(params),
  });
}

export function useEmployee(employeeId: string) {
  return useQuery({
    queryKey: queryKeys.employees.detail(employeeId),
    queryFn: () => fetchEmployee(employeeId),
    enabled: Boolean(employeeId),
  });
}

export function useEmployeeAllocations(employeeId: string, page: number, pageSize: number) {
  return useQuery({
    queryKey: queryKeys.employees.allocations(employeeId, page, pageSize),
    queryFn: () => fetchEmployeeAllocations(employeeId, page, pageSize),
    enabled: Boolean(employeeId),
  });
}

export function useEmployeeMutations() {
  const queryClient = useQueryClient();

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["employees"] });
    queryClient.invalidateQueries({ queryKey: queryKeys.dashboard.summary });
  };

  return {
    create: useMutation({ mutationFn: createEmployee, onSuccess: invalidate }),
    update: useMutation({
      mutationFn: ({ id, data }: { id: string; data: EmployeeUpdate }) => updateEmployee(id, data),
      onSuccess: invalidate,
    }),
    deactivate: useMutation({ mutationFn: deactivateEmployee, onSuccess: invalidate }),
  };
}
