import React, { useEffect, useState } from "react";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { ANONYMOUS_USER, CsrfContext, CurrentUserContext } from "./context";
import routes from "./routes";

const queryClient = new QueryClient();
const router = createBrowserRouter(routes);

export default function App() {
  const [csrfToken, setCsrfToken] = useState("");
  const [currentUser, setCurrentUser] = useState(ANONYMOUS_USER);

  useEffect(() => {
    (async () => {
      try {
        const result = await fetch("/$api/csrf-token");
        const data = await result.json();
        setCsrfToken(data.csrfToken);
      } catch (err) {
        setCsrfToken("");
      }
    })();
  }, []);

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
  }, []);

  return (
    <React.StrictMode>
      <CsrfContext.Provider value={csrfToken}>
        <CurrentUserContext.Provider value={currentUser}>
          <QueryClientProvider client={queryClient}>
            <RouterProvider router={router} />
          </QueryClientProvider>
        </CurrentUserContext.Provider>
      </CsrfContext.Provider>
    </React.StrictMode>
  );
}
