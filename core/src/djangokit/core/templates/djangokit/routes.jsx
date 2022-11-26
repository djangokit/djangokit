{% for layout_info in routes %}
// ==== Layout: {{ layout_info.id }} @ {{ layout_info.route_pattern }}
import { default as Layout_{{ layout_info.id }} } from "../../routes/{{ layout_info.import_path }}";
{% for page_info in layout_info.children %}
// ---- Page: {{ page_info.id }} @ {{ page_info.route_pattern }}
import { default as Page_{{ page_info.id }} } from "../../routes/{{ page_info.import_path }}";
{% endfor %}{% endfor %}

const routes = [{% for layout_info in routes %}
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
];

export default routes;
