import React from "react";
import { createRoot, hydrateRoot } from 'react-dom/client';
import { Route, Routes, BrowserRouter } from "react-router-dom";
{% load djangokit %}
{% route_imports routes %}
const routes = [
  {% browser_router_entries routes %}
];

// Set to false to disable hydration and use client side rendering.
const HYDRATE = true;

const rootElement = document.getElementById("root");

const App = () => {
  return (
    <React.StrictMode>
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
    </React.StrictMode>
  );
};

if (HYDRATE) {
  hydrateRoot(rootElement, <App />);
} else {
  createRoot(rootElement).render(<App />);
}
