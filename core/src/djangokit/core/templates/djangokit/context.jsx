import React, { createContext, useContext } from "react";

// CSRF ----------------------------------------------------------------

export const CsrfContext = createContext("{{ csrf_token }}");

export function useCsrfContext() {
  return useContext(CsrfContext);
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
