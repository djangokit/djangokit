import React from "react";
import ReactDOM from "react-dom/client";

import { createBrowserRouter, RouterProvider } from "react-router-dom";
{% for layout_info in imports %}
// ==== Layout: {{ layout_info.id }} @ {{ layout_info.route_pattern }}
import {{ layout_info.what }} from "{{ layout_info.path }}";
{% for page_info in layout_info.children %}
// ---- Page: {{ page_info.id }} @ {{ page_info.route_pattern }}
import {{ page_info.what }} from "{{ page_info.path }}";
{% endfor %}{% endfor %}
const router = createBrowserRouter([{% for layout_info in routes %}
  // ==== Layout: {{ layout_info.id }}
  {
    path: "{{ layout_info.route_pattern }}",
    element: <Layout_{{ layout_info.id }} />,
    children: [{% for page_info in layout_info.children %}
      // ---- Page: {{ page_info.id }}
      {
        path: "{{ page_info.layout_route_pattern }}",
        element: <Page_{{ page_info.id }} />,
      },{% endfor %}
    ],
  },{% endfor %}
]);

const rootElement = document.getElementById("root");

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);
