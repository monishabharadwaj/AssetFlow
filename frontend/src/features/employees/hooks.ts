import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import type { EmployeeCreate, EmployeeUpdate } from "@/lib/types/backend";
import { createEmployee, deactivateEmployee, fetchEmployees, updateEmployee } from "./api";

export function useEmployees(params: { page?: number; page_size?: number; search?: string; department_id?: string } = {}) {
  return useQuery({
    queryKey: ["employees", params],
    queryFn: () => fetchEmployees(params),
  });
}

export function useCreateEmployee() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: EmployeeCreate) => createEmployee(data),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ["employees"] }),
  });
}

export function useUpdateEmployee() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: EmployeeUpdate }) => updateEmployee(id, data),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ["employees"] }),
  });
}

export function useDeactivateEmployee() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deactivateEmployee(id),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ["employees"] }),
  });
}
