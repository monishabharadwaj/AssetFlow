import { useCallback, useMemo } from "react";
import { useSearchParams } from "react-router-dom";

export function useUrlSearchParams<T extends Record<string, string | number | boolean | undefined>>(
  defaults: T,
) {
  const [searchParams, setSearchParams] = useSearchParams();

  const params = useMemo(() => {
    const result = { ...defaults };
    for (const key of Object.keys(defaults)) {
      const raw = searchParams.get(key);
      if (raw === null) continue;
      const defaultVal = defaults[key];
      if (typeof defaultVal === "number") {
        (result as Record<string, unknown>)[key] = Number(raw) || defaultVal;
      } else if (typeof defaultVal === "boolean") {
        (result as Record<string, unknown>)[key] = raw === "true";
      } else {
        (result as Record<string, unknown>)[key] = raw;
      }
    }
    return result;
  }, [searchParams, defaults]);

  const setParams = useCallback(
    (updates: Partial<T>) => {
      const next = new URLSearchParams(searchParams);
      for (const [key, value] of Object.entries(updates)) {
        if (value === undefined || value === "" || value === defaults[key as keyof T]) {
          next.delete(key);
        } else {
          next.set(key, String(value));
        }
      }
      setSearchParams(next, { replace: true });
    },
    [searchParams, setSearchParams, defaults],
  );

  return [params, setParams] as const;
}
