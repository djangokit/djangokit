import React from "react";
import {
  unstable_createStaticRouter,
  unstable_StaticRouterProvider as RouterProvider,
} from "react-router-dom/server";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import routes from "./routes";

const queryClient = new QueryClient();

const routerContext = { location: "{{ request.path }}" };
const router = unstable_createStaticRouter(routes, routerContext);

export default function App() {
  return (
    <React.StrictMode>
      <QueryClientProvider client={queryClient}>
        <RouterProvider router={router} context={routerContext} />
      </QueryClientProvider>
    </React.StrictMode>
  );
}
