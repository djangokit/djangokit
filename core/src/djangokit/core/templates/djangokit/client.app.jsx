import { CookiesProvider, useCookies } from "react-cookie";
import React, { useEffect, useState } from "react";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { ANONYMOUS_USER, CsrfContext, CurrentUserContext } from "./context";
import routes from "./routes";

const queryClient = new QueryClient();
const router = createBrowserRouter(routes);

export default function App() {
  return (
    <React.StrictMode>
      <CookiesProvider>
        <Auth>
          <QueryClientProvider client={queryClient}>
            <RouterProvider router={router} />
          </QueryClientProvider>
        </Auth>
      </CookiesProvider>
    </React.StrictMode>
  );
}

function Auth({ children }) {
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
        const result = await fetch("/$api/current-user");
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
