import React, { useEffect, useState } from "react";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { ANONYMOUS_USER, CurrentUserContext } from "./context";
import routes from "./routes";

const queryClient = new QueryClient();
const browserRouter = createBrowserRouter(routes);

export default function ClientApp() {
  const [currentUser, setCurrentUser] = useState(ANONYMOUS_USER);

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
      <CurrentUserContext.Provider value={currentUser}>
        <QueryClientProvider client={queryClient}>
          <RouterProvider router={browserRouter} />
        </QueryClientProvider>
      </CurrentUserContext.Provider>
    </React.StrictMode>
  );
}
