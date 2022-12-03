import React from "react";
import {
  unstable_createStaticRouter,
  unstable_StaticRouterProvider as RouterProvider,
} from "react-router-dom/server";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { ANONYMOUS_USER, CsrfContext, CurrentUserContext } from "./context";
import routes from "./routes";

const REQUEST_PATH = process.argv[2] || "/";
const CSRF_TOKEN = process.argv[3] || "__csrf_token__";
const CURRENT_USER = process.argv[4]
  ? JSON.parse(process.argv[4])
  : ANONYMOUS_USER;

const queryClient = new QueryClient();
const routerContext = { location: REQUEST_PATH };
const router = unstable_createStaticRouter(routes, routerContext);

export default function App() {
  return (
    <React.StrictMode>
      <CsrfContext.Provider value={CSRF_TOKEN}>
        <CurrentUserContext.Provider value={CURRENT_USER}>
          <QueryClientProvider client={queryClient}>
            <RouterProvider router={router} context={routerContext} />
          </QueryClientProvider>
        </CurrentUserContext.Provider>
      </CsrfContext.Provider>
    </React.StrictMode>
  );
}
