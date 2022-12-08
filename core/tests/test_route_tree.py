import pytest

from djangokit.core.routes import RouteDirNode, make_route_dir_tree


@pytest.fixture
def tree():
    tree = make_route_dir_tree()
    return tree


def test_make_route_dir_tree(tree):
    assert tree.root


def test_traversal(tree):
    def visitor(node: RouteDirNode):
        if node.has_page:
            ids.append(node.id)

    ids = []
    tree.traverse(visit=visitor)
    assert ids == ["$root", "docs", "docs__slug", "_slug", "catchall"]


def test_collect_page_nodes(tree):
    nodes = tree.collect_page_nodes()
    ids = [node.id for node in nodes]
    assert ids == ["$root", "docs", "docs__slug", "_slug", "catchall"]


def test_collect_api_nodes(tree):
    nodes = tree.collect_api_nodes()
    ids = [node.id for node in nodes]
    assert ids == ["$root", "_slug", "catchall"]


def test_js_routes(tree):
    routes = tree.js_routes(serialize=False)
    assert len(routes) == 2
