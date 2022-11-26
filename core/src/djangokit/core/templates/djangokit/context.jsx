import React, { createContext, useContext } from "react";

// CSRF ----------------------------------------------------------------

export const CSRF_TOKEN = "{{ csrf_token }}";
export const CsrfContext = createContext("{{ csrf_token }}");

export function useCsrfContext() {
  return useContext(CsrfContext);
}

/**
 * Renders a hidden input field with the CSRF token.
 */
export function CsrfTokenField() {
  const csrfToken = useCsrfContext();
  return <input type="hidden" name="csrfmiddlewaretoken" value={csrfToken} />;
}

// User ----------------------------------------------------------------

export const ANONYMOUS_USER = {
  username: null,
  email: null,
  isAnonymous: true,
  isAuthenticated: false,
  isStaff: false,
  isSuperuser: false,
};

export const CurrentUserContext = createContext(ANONYMOUS_USER);

export function useCurrentUserContext() {
  return useContext(CurrentUserContext);
}
