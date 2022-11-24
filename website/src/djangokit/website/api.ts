import * as query from "@tanstack/react-query";
import { Page } from "./models";

const API_ROOT = "/$api";

class ApiError extends Error {
  constructor(message: string, public response?: any) {
    super(message);
  }

  get statusCode(): number | undefined {
    return this.response?.status;
  }
}

/**
 * API fetch wrapper.
 *
 * @param path API path, relative to API root
 * @param options Fetch options
 * @throws {ApiError | AbortError}
 */
export async function apiFetch<M>(path: string, options?: RequestInit) {
  if (path.charAt(0) === "/") {
    path = path.substring(1);
  }
  const url = path === "" ? API_ROOT : `${API_ROOT}/${path}`;

  let response;

  try {
    response = await fetch(url, options);
  } catch (fetchErr) {
    // NOTE: fetch() can also throw an AbortError, which we don't want
    //       to catch.
    if (fetchErr instanceof TypeError) {
      throw new ApiError(fetchErr.message.replace(/\.$/, ""));
    }
    throw fetchErr;
  }

  // The response is not okay when its status >= 300.
  if (!response.ok) {
    throw new ApiError(response.statusText, response);
  }

  try {
    const data: M = await response.json();
    return data;
  } catch (jsonErr) {
    throw new ApiError("Could not parse JSON from response", response);
  }
}

/**
 * Hook to fetch a Page (wraps react-query's useQuery).
 *
 * @param slug Slug for page (e.g. "home")
 */
export function usePageQuery(
  slug: string
): ReturnType<typeof query.useQuery<Page, ApiError>> {
  return query.useQuery<Page, ApiError>({
    queryKey: [`page-${slug}`],
    retry: false,
    queryFn: async () => await apiFetch<Page>(slug),
  });
}
