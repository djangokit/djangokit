import React from "react";
import ReactDOM from "react-dom/client";

import { createBrowserRouter, RouterProvider } from "react-router-dom";

const router = createBrowserRouter([
  {% for info in page_info %}
    {
      path: "{{ info.route_pattern }}",
      element: <div>{'{{ info.route_pattern }}'}</div>,
    },
  {% endfor %}
]);

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <RouterProvider router={router}/>
  </React.StrictMode>
);
