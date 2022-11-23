from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def route_imports(routes: list, import_prefix="../../routes") -> str:
    lines = []

    for layout_info in routes:
        layout_id = layout_info.id
        import_path = f"{import_prefix}/{layout_info.import_path}"
        pattern = layout_info.route_pattern
        component_name = f"Layout_{layout_id}"

        lines.append(f"// ==== Layout: {layout_id} @ {pattern}")
        lines.append(f'import {{ default as {component_name} }} from "{import_path}";')

        for page_info in layout_info.children:
            page_id = page_info.id
            import_path = f"{import_prefix}/{page_info.import_path}"
            pattern = page_info.route_pattern
            component_name = f"Page_{page_id}"

            lines.append(f"// ---- Page: {page_id} @ {pattern}")
            lines.append(
                f'import {{ default as {component_name} }} from "{import_path}";'
            )

        lines.append("")

    return mark_safe("\n".join(lines))


@register.simple_tag
def browser_router_entries(routes: list) -> str:
    entries = []

    for layout_info in routes:
        children = [
            PAGE_ENTRY_TEMPLATE.format(info=info) for info in layout_info.children
        ]
        children = "\n".join(children)
        entry = LAYOUT_ENTRY_TEMPLATE.format(info=layout_info, children=children)
        entries.append(entry)

    return mark_safe("\n".join(entries))


LAYOUT_ENTRY_TEMPLATE = """\
  // ==== Layout: {info.id}
  {{
    path: "{info.route_pattern}",
    element: <Layout_{info.id} />,
    children: [
{children}
    ],
  }},\
"""

PAGE_ENTRY_TEMPLATE = """\
      // ---- Page: {info.id}
      {{
        path: "{info.layout_route_pattern}",
        element: <Page_{info.id} />,
      }},\
"""
