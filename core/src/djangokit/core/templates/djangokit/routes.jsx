/* eslint-disable */
{% for i in route_info.imports %}{{ i|safe }}
{% endfor %}
const routes = [
{{ route_info.routes|safe }}];

export default routes;
