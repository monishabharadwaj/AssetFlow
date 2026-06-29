import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import type { DepartmentCreate, DepartmentUpdate } from "@/lib/types/backend";
import { createDepartment, deactivateDepartment, fetchDepartments, updateDepartment } from "./api";

export function useDepartments(
  params: { page?: number; page_size?: number; search?: string } = {},
  enabled = true,
) {
  return useQuery({
    queryKey: ["departments", params],
    queryFn: () => fetchDepartments(params),
    enabled,
  });
}

export function useCreateDepartment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: DepartmentCreate) => createDepartment(data),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ["departments"] }),
  });
}

export function useUpdateDepartment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: DepartmentUpdate }) => updateDepartment(id, data),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ["departments"] }),
  });
}

export function useDeactivateDepartment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => deactivateDepartment(id),
    onSuccess: () => void qc.invalidateQueries({ queryKey: ["departments"] }),
  });
}
