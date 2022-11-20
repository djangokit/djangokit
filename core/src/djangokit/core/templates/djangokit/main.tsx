import React from "react";
import ReactDOM from "react-dom/client";

import { createBrowserRouter, RouterProvider } from "react-router-dom";

{% for info in imports %}import {{ info.what }} from "{{ info.path }}";{% endfor %}

const router = createBrowserRouter([
  {% for info in page_info %}
    {
      path: "{{ info.route_pattern }}",
      element: <Page_{{ info.id }} data={% verbatim %}{{}}{% endverbatim %} />,
    },
  {% endfor %}
]);

const rootElement = document.getElementById("root");

ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <RouterProvider router={router}/>
  </React.StrictMode>
);
