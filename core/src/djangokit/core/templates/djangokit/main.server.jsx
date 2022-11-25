import React from "react";
import ReactDOMServer from "react-dom/server";
import { Route, Routes } from "react-router-dom";
import { StaticRouter } from "react-router-dom/server";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
{% load djangokit %}
{% route_imports routes %}
const routes = [
  {% browser_router_entries routes %}
];

const queryClient = new QueryClient();

const App = () => {
  return (
    <React.StrictMode>
      <QueryClientProvider client={queryClient}>
        <StaticRouter location={"{{ request.path }}"}>
          <Routes>
            {routes.map(({ path, element, children }) => {
              return <Route key={path} path={path} element={element}>
                {children.map(({ path, element }) => {
                  return <Route key={path} path={path} element={element}/>
                })}
              </Route>
            })}
          </Routes>
        </StaticRouter>
      </QueryClientProvider>
    </React.StrictMode>
  );
}

const html = ReactDOMServer.renderToString(<App />);

console.log(html.trim());
