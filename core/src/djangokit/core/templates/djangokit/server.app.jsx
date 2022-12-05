import React from "react";
import {
  unstable_createStaticRouter,
  unstable_StaticRouterProvider as RouterProvider,
} from "react-router-dom/server";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { ANONYMOUS_USER, CsrfContext, CurrentUserContext } from "./context";
import routes from "./routes";

const location = process.argv[2] || "/";
const csrfToken = process.argv[3] || "__csrf_token__";
const currentUser = process.argv[4]
  ? JSON.parse(process.argv[4])
  : ANONYMOUS_USER;

const queryClient = new QueryClient();
const routerContext = { location };
const router = unstable_createStaticRouter(routes, routerContext);

export default function App() {
  return (
    <React.StrictMode>
      <Auth>
        <QueryClientProvider client={queryClient}>
          <RouterProvider router={router} context={routerContext} />
        </QueryClientProvider>
      </Auth>
    </React.StrictMode>
  );
}

function Auth({ children }) {
  return (
    <CsrfContext.Provider value={csrfToken}>
      <CurrentUserContext.Provider value={currentUser}>
        {children}
      </CurrentUserContext.Provider>
    </CsrfContext.Provider>
  );
}
