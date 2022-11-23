import React from "react";
import ReactDOM from "react-dom";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
{% load djangokit %}
{% route_imports routes %}
const router = createBrowserRouter([
{% browser_router_entries routes %}
]);

const root = document.getElementById("root");

ReactDOM.hydrate(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
  root,
);
