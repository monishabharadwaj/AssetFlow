import { toast as sonnerToast } from "sonner";

export function toast(message: string, type: "success" | "error" = "success") {
  if (type === "error") sonnerToast.error(message);
  else sonnerToast.success(message);
}
