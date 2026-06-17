export const queryKeys = {
  dashboard: {
    summary: ["dashboard", "summary"] as const,
  },
  assets: {
    list: (params: Record<string, unknown>) => ["assets", "list", params] as const,
    search: (params: Record<string, unknown>) => ["assets", "search", params] as const,
    detail: (assetId: string) => ["assets", "detail", assetId] as const,
    timeline: (assetId: string, page: number, pageSize: number) =>
      ["assets", "timeline", assetId, page, pageSize] as const,
    allocations: (assetId: string, page: number, pageSize: number) =>
      ["assets", "allocations", assetId, page, pageSize] as const,
    transfers: (assetId: string, page: number, pageSize: number) =>
      ["assets", "transfers", assetId, page, pageSize] as const,
    maintenance: (assetId: string, page: number, pageSize: number) =>
      ["assets", "maintenance", assetId, page, pageSize] as const,
    health: (assetId: string, page: number, pageSize: number) =>
      ["assets", "health", assetId, page, pageSize] as const,
  },
  departments: {
    list: (params: Record<string, unknown>) => ["departments", "list", params] as const,
    detail: (departmentId: string) => ["departments", "detail", departmentId] as const,
  },
  employees: {
    list: (params: Record<string, unknown>) => ["employees", "list", params] as const,
    detail: (employeeId: string) => ["employees", "detail", employeeId] as const,
    allocations: (employeeId: string, page: number, pageSize: number) =>
      ["employees", "allocations", employeeId, page, pageSize] as const,
  },
  lookups: {
    categories: ["lookups", "categories"] as const,
    types: ["lookups", "types"] as const,
  },
  maintenance: {
    detail: (recordId: string) => ["maintenance", "detail", recordId] as const,
  },
};
