import React from "react";
import { Route, Routes } from "react-router-dom";
import { StaticRouter } from "react-router-dom/server";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import routes from "./routes";

const queryClient = new QueryClient();

export default function ServerApp() {
  return (
    <React.StrictMode>
      <QueryClientProvider client={queryClient}>
        <StaticRouter location={"{{ request.path }}"}>
          <Routes>
            {routes.map(({ path, element, children }) => {
              return (
                <Route key={path} path={path} element={element}>
                  {children.map(({ path, element }) => {
                    return <Route key={path} path={path} element={element} />;
                  })}
                </Route>
              );
            })}
          </Routes>
        </StaticRouter>
      </QueryClientProvider>
    </React.StrictMode>
  );
}
