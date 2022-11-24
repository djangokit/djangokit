import React from "react";
import { createRoot, hydrateRoot } from 'react-dom/client';
import { Route, Routes, BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
{% load djangokit %}
{% route_imports routes %}
const routes = [
  {% browser_router_entries routes %}
];

const queryClient = new QueryClient()

const App = () => {
  return (
    <React.StrictMode>
      <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          {routes.map(({ path, element, children }) => {
            return <Route key={path} path={path} element={element}>
              {children.map(({ path, element }) => {
                return <Route key={path} path={path} element={element} />
              })}
            </Route>
          })}
        </Routes>
      </BrowserRouter>
      </QueryClientProvider>
    </React.StrictMode>
  );
};

const rootElement = document.getElementById("root");

// Set this to false to do client side rendering.
const SSR = true;

if (SSR) {
  hydrateRoot(rootElement, <App/>);
} else {
  createRoot(rootElement).render(<App/>)
}
