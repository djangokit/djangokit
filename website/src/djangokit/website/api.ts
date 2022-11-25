import { useQuery } from "@tanstack/react-query";

import { Page } from "./models";

declare global {
  const CSRF_TOKEN: string;
}

const API_ROOT = "/$api";

class ApiError extends Error {
  constructor(message: string, public response?: any) {
    super(message);
  }

  get statusCode(): number | undefined {
    return this.response?.status;
  }
}

type Params = Record<string, unknown>;

interface Options extends RequestInit {
  params?: Params;
  data?: Params;
}

/**
 * Given a relative API URL, return a URL object.
 *
 * @param path API path, relative to API root
 * @param params Query parameters
 */
function getApiUrl(apiPath: string, params?: Params): URL {
  if (apiPath.charAt(0) === "/") {
    apiPath = apiPath.substring(1);
  }
  apiPath = apiPath === "" ? API_ROOT : `${API_ROOT}/${apiPath}`;
  const url = new URL(`${location.origin}${apiPath}`);
  if (params) {
    Object.entries(params).forEach(([name, value]) => {
      url.searchParams.append(name, `${value}`);
    });
  }
  return url;
}

const api = {
  /**
   * API fetch wrapper.
   *
   * @param path API path, relative to API root
   * @param options Fetch options
   * @throws {ApiError | AbortError}
   */
  async fetch<M>(path: string, options?: Options) {
    options = options ?? {};

    options.headers = options.headers ?? {};
    options.headers["X-CSRFToken"] = CSRF_TOKEN;

    if (options.data) {
      options.body = JSON.stringify(options.data);
    }

    const url = getApiUrl(path, options.params);

    let response;

    try {
      response = await fetch(url, options);
    } catch (fetchErr) {
      // NOTE: fetch() can also throw an AbortError, which we don't want
      //       to catch here.
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
  },

  async delete<M>(path: string) {
    return this.fetch<M>(path, { method: "DELETE" });
  },

  async patch<M>(path: string, data: any) {
    return this.fetch<M>(path, { method: "PATCH", data });
  },

  async post<M>(path: string, data: any) {
    return this.fetch<M>(path, { method: "POST", data });
  },

  async put<M>(path: string, data: any) {
    return this.fetch<M>(path, { method: "PUT", data });
  },
};

export default api;

/**
 * Hook to fetch data from API (wraps react-query's useQuery).
 *
 * @param path API path passed through to `apiFetch()`
 * @param queryKey
 */
export function useApiQuery<M>(
  path: string,
  queryKey?: any
): ReturnType<typeof useQuery<M, ApiError>> {
  return useQuery<any, ApiError>({
    queryKey: queryKey ?? [path],
    retry: false,
    queryFn: async () => await api.fetch(path),
  });
}

/**
 * Hook to fetch a Page (wraps react-query's useQuery).
 *
 * @param slug Slug for page (e.g. "home")
 */
export function usePageQuery(
  slug: string
): ReturnType<typeof useQuery<Page, ApiError>> {
  return useQuery<Page, ApiError>({
    queryKey: [`page-${slug}`],
    retry: false,
    queryFn: async () => await api.fetch<Page>(slug),
  });
}
