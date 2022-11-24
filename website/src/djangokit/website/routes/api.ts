import { useEffect, useState } from "react";

const API_ROOT = "/$api";

export interface Error {
  statusCode: number;
  message: string;
}

interface Options {
  method: string;
}

/**
 * useEffect hook for fetching API data.
 *
 * @param path
 * @param options
 */
export function useApi<D>(
  path: string,
  options: Options = { method: "GET" },
  dependencies: unknown[] = []
): [D | null, Error | null] {
  if (path.charAt(0) === "/") {
    path = path.substring(1);
  }

  const url = path === "" ? API_ROOT : `${API_ROOT}/${path}`;

  const [data, setData] = useState<D | null>(null);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    (async () => {
      let response;

      try {
        response = await fetch(url, options);
      } catch (err) {
        setData(null);
        setError({
          statusCode: -1,
          message: (err as Error).message,
        });
        return;
      }

      const status = response.status;

      let data: D;

      try {
        data = await response.json();
      } catch (err) {
        setData(null);
        setError({
          statusCode: status,
          message: (err as Error).message,
        });
        return;
      }

      setData(data);
      setError(null);
    })();
  }, dependencies);

  return [data, error];
}
