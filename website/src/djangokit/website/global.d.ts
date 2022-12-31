export {};

declare global {
  const ENV: string;
  const useCsrfContext: () => string;
  const useCurrentUserContext: () => any;
}
