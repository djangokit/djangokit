import pytest
from djangokit.core.routes import RouteNode, make_route_dir_tree


@pytest.fixture
def tree():
    return make_route_dir_tree()


@pytest.fixture
def expected_node_ids():
    return ["$root", "docs", "docs__slug", "_slug", "catchall"]


def test_make_route_dir_tree(tree):
    assert tree.root


def test_traversal(tree, expected_node_ids):
    def visitor(node: RouteNode):
        if node.page_module:
            ids.append(node.id)

    ids = []
    tree.traverse(visit=visitor)
    assert ids == expected_node_ids


def test_iter(tree, expected_node_ids):
    nodes = tuple(tree)
    assert [node.id for node in nodes] == expected_node_ids


def test_js_routes(tree):
    routes = tree.js_routes(serialize=False)
    assert len(routes) == 2
