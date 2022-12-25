from djangokit.core.routes import make_route_dir_tree
from djangokit.core.views import RouteView


def test_view_handlers():
    tree = make_route_dir_tree()
    view = RouteView.as_view_from_node(tree.root)
    assert hasattr(view, "djangokit_handlers")
    handlers = view.djangokit_handlers

    # GET
    assert "get" in handlers
    get_handlers = handlers["get"]

    assert "" in get_handlers
    get_handler = get_handlers[""]
    assert get_handler.is_loader

    assert "stuff" in get_handlers
    stuff_handler = get_handlers["stuff"]
    assert not stuff_handler.is_loader
    assert stuff_handler.cache_time == 5
    assert stuff_handler.vary_on == ()

    assert "things" in get_handlers
    things_handler = get_handlers["things"]
    assert not things_handler.is_loader
    assert things_handler.cache_time == 10
    assert things_handler.vary_on == ["Accept"]

    assert "private" in get_handlers
    private_handler = get_handlers["private"]
    assert not private_handler.is_loader
    assert private_handler.cache_time == 0
    assert private_handler.private

    # HEAD
    assert "head" in handlers
    head_handlers = handlers["head"]
    assert "" in head_handlers
    assert head_handlers[""] is get_handlers[""]


def test_view_handler_caching(client):
    response = client.get("/stuff")
    assert response.status_code == 200

    # Cache
    assert "Cache-Control" in response
    assert "Expires" in response
    assert response["Cache-Control"] == "public, max-age=5"

    # Vary
    assert "Vary" not in response

    # Data
    assert "Content-Type" in response
    assert response["Content-Type"] == "application/json"
    data = response.json()
    assert data == {"slug": "stuff"}


def test_view_handler_caching_and_vary_on(client):
    response = client.get("/things")
    assert response.status_code == 200

    # Cache
    assert "Cache-Control" in response
    assert "Expires" in response
    assert response["Cache-Control"] == "public, max-age=10"

    # Vary
    assert "Vary" in response
    assert response["Vary"] == "Accept"

    # Data
    assert "Content-Type" in response
    assert response["Content-Type"] == "application/json"
    data = response.json()
    assert data == {"slug": "things"}


def test_view_handler_private_caching(client):
    response = client.get("/private")
    assert response.status_code == 200

    # Cache
    assert "Cache-Control" in response
    assert "Expires" not in response
    assert response["Cache-Control"] == "private"

    # Vary
    assert "Vary" not in response

    # Data
    assert "Content-Type" in response
    assert response["Content-Type"] == "application/json"
    data = response.json()
    assert data == {"slug": "private"}
