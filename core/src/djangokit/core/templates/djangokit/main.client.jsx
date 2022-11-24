import React from "react";
import { createRoot, hydrateRoot } from 'react-dom/client';
import { Route, Routes, BrowserRouter } from "react-router-dom";
{% load djangokit %}
{% route_imports routes %}
const routes = [
  {% browser_router_entries routes %}
];

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

const rootElement = document.getElementById("root");

// Set this to false to do client side rendering.
const SSR = true;

if (SSR) {
  hydrateRoot(rootElement, <App/>);
} else {
  createRoot(rootElement).render(<App/>)
}
