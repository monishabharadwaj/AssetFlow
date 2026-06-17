export function formatCurrency(value: string | number): string {
  const num = typeof value === "string" ? parseFloat(value) : value;
  return new Intl.NumberFormat(undefined, { style: "currency", currency: "USD" }).format(num);
}

export function formatDate(value: string | null | undefined): string {
  if (!value) return "—";
  return new Date(value).toLocaleDateString(undefined, { dateStyle: "medium" });
}

export function employeeName(employee: { first_name: string; last_name: string }): string {
  return `${employee.first_name} ${employee.last_name}`;
}
