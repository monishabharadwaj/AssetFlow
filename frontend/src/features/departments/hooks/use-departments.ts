import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { queryKeys } from "../../../shared/api/query-keys";
import type { DepartmentCreate, DepartmentListParams, DepartmentUpdate } from "../../../shared/api/types";
import {
  createDepartment,
  deactivateDepartment,
  fetchDepartment,
  fetchDepartments,
  updateDepartment,
} from "../api/departments-api";

export function useDepartmentsList(params: DepartmentListParams = { page: 1, page_size: 100 }) {
  return useQuery({
    queryKey: queryKeys.departments.list(params),
    queryFn: () => fetchDepartments(params),
  });
}

export function useDepartment(departmentId: string) {
  return useQuery({
    queryKey: queryKeys.departments.detail(departmentId),
    queryFn: () => fetchDepartment(departmentId),
    enabled: Boolean(departmentId),
  });
}

export function useDepartmentMutations() {
  const queryClient = useQueryClient();

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["departments"] });
    queryClient.invalidateQueries({ queryKey: queryKeys.dashboard.summary });
  };

  return {
    create: useMutation({ mutationFn: createDepartment, onSuccess: invalidate }),
    update: useMutation({
      mutationFn: ({ id, data }: { id: string; data: DepartmentUpdate }) => updateDepartment(id, data),
      onSuccess: invalidate,
    }),
    deactivate: useMutation({ mutationFn: deactivateDepartment, onSuccess: invalidate }),
  };
}
