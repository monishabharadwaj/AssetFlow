import { useEffect } from "react";

import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useDepartments } from "@/features/departments/hooks";
import { MAX_PAGE_SIZE } from "@/lib/constants";
import { toast } from "@/lib/toast";

type Props = {
  value: string;
  onChange: (id: string) => void;
  label?: string;
  required?: boolean;
  disabled?: boolean;
  enabled?: boolean;
};

export function DepartmentSelect({
  value,
  onChange,
  label = "Department",
  required,
  disabled,
  enabled = true,
}: Props) {
  const query = useDepartments({ page: 1, page_size: MAX_PAGE_SIZE }, enabled);
  const items = query.data?.items ?? [];

  useEffect(() => {
    if (query.isError) {
      toast((query.error as Error).message, "error");
    }
  }, [query.isError, query.error]);

  return (
    <div className="space-y-1.5">
      <Label>{label}{required ? " *" : ""}</Label>
      <Select
        value={value || undefined}
        onValueChange={onChange}
        disabled={disabled || query.isLoading || query.isError}
      >
        <SelectTrigger className="w-full">
          <SelectValue
            placeholder={
              query.isLoading
                ? "Loading departments…"
                : query.isError
                  ? "Failed to load departments"
                  : items.length === 0
                    ? "No departments found"
                    : "Select department…"
            }
          />
        </SelectTrigger>
        <SelectContent>
          {items.map((d) => (
            <SelectItem key={d.id} value={d.id}>
              {d.name}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}
