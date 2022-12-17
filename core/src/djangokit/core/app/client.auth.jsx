import React, { useEffect, useState } from "react";
import { useCookies } from "react-cookie";

import { ANONYMOUS_USER, CsrfContext, CurrentUserContext } from "./context";

export default function Auth({ children }) {
  const [cookies] = useCookies(["csrftoken", "sessionid"]);
  const [csrfToken, setCsrfToken] = useState("");
  const [currentUser, setCurrentUser] = useState(ANONYMOUS_USER);

  useEffect(
    () => setCsrfToken(cookies["csrftoken"] ?? "__csrf_token__"),
    [cookies]
  );

  useEffect(() => {
    (async () => {
      try {
        const result = await fetch("/{{ settings.api_prefix }}current-user");
        const data = await result.json();
        setCurrentUser(data);
      } catch (err) {
        setCurrentUser(ANONYMOUS_USER);
      }
    })();
  }, [cookies]);

  return (
    <CsrfContext.Provider value={csrfToken}>
      <CurrentUserContext.Provider value={currentUser}>
        {children}
      </CurrentUserContext.Provider>
    </CsrfContext.Provider>
  );
}
