export {};

declare global {
  const DEBUG: boolean;
  const ENV: string;
  const useCsrfContext: () => string;
  const useCurrentUserContext: () => any;
}
