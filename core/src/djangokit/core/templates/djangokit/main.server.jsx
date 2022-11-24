import React from "react";
import ReactDOMServer from "react-dom/server";
import { Route, Routes } from "react-router-dom";
import { StaticRouter } from "react-router-dom/server";
{% load djangokit %}
{% route_imports routes %}
const routes = [
  {% browser_router_entries routes %}
];

const App = () => {
  return (
    <React.StrictMode>
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
    </React.StrictMode>
  );
}

const html = ReactDOMServer.renderToString(<App />);

console.log(html.trim());
