const API_ROOT = "/$api";

export interface Error {
  statusCode: number;
  message: string;
}

/**
 * API fetch wrapper.
 *
 * @param path API path, relative to API root
 * @param options Fetch options
 */
export async function apiFetch(path: string, options?: RequestInit) {
  if (path.charAt(0) === "/") {
    path = path.substring(1);
  }
  const url = path === "" ? API_ROOT : `${API_ROOT}/${path}`;
  const response = await fetch(url, options);
  if (!response.ok) {
    throw new Error(response.statusText);
  }
  return response.json();
}
