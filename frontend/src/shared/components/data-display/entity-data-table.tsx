import type { ReactNode } from "react";

import { Skeleton } from "../ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../ui/table";

export type ColumnDef<T> = {
  id: string;
  header: string;
  cell: (row: T) => ReactNode;
  className?: string;
};

type EntityDataTableProps<T> = {
  columns: ColumnDef<T>[];
  data: T[];
  isLoading?: boolean;
  emptyMessage?: string;
  rowKey: (row: T) => string;
};

export function EntityDataTable<T>({
  columns,
  data,
  isLoading,
  emptyMessage = "No records found.",
  rowKey,
}: EntityDataTableProps<T>) {
  if (isLoading) {
    return (
      <div className="space-y-3 rounded-3xl border border-slate-700 bg-[#111827] p-6 shadow-[0_0_20px_rgba(59,130,246,0.10)]">
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className="h-10 w-full" />
        ))}
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="rounded-3xl border border-slate-700 bg-[#111827] p-10 text-center text-sm text-slate-400 shadow-[0_0_20px_rgba(59,130,246,0.10)]">
        {emptyMessage}
      </div>
    );
  }

  return (
    <div className="rounded-lg border">
      <Table>
        <TableHeader>
          <TableRow>
            {columns.map((col) => (
              <TableHead
                key={col.id}
                className={`bg-[#0f172a] text-slate-300 font-semibold uppercase tracking-wider ${col.className ?? ""}`}
              >
                {col.header}
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.map((row) => (
            <TableRow
              key={rowKey(row)}
              className="border-slate-700 transition-all duration-300 hover:bg-blue-500/10 hover:shadow-[inset_0_0_12px_rgba(59,130,246,0.12)]"
            >
              {columns.map((col) => (
                <TableCell
                  key={col.id}
                  className={`py-4 text-slate-200 ${col.className ?? ""}`}
                >
                  {col.cell(row)}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
