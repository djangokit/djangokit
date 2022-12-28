from djangokit.core.routes import make_route_dir_tree
from djangokit.core.views import RouteView


def test_view_handlers():
    tree = make_route_dir_tree()
    view = RouteView.as_view_from_node(tree.root)
    assert "handlers" in view.view_initkwargs
    handlers = view.view_initkwargs["handlers"]

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
    assert stuff_handler.vary_on == ("Accept",)

    assert "things" in get_handlers
    things_handler = get_handlers["things"]
    assert not things_handler.is_loader
    assert things_handler.cache_time == 10
    assert things_handler.vary_on == ["Accept", "Accept-Language"]

    assert "private" in get_handlers
    private_handler = get_handlers["private"]
    assert not private_handler.is_loader
    assert private_handler.cache_time is None
    assert private_handler.private

    # HEAD
    assert "head" in handlers
    head_handlers = handlers["head"]
    assert "" in head_handlers
    assert head_handlers[""] is get_handlers[""]


def test_get(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response["Content-Type"] != "application/json"


def test_get_with_ext(client):
    response = client.get("/stuff.ext")
    assert response.status_code == 200
    check_data(response, {"slug": "stuff", "ext": "ext"})


def test_get_with_unknown_ext(client):
    # This will trigger the catchall handler
    response = client.get("/stuff.UNKNOWN_EXT")
    assert response.status_code == 404


def check_data(response, expected_data):
    assert "Content-Type" in response
    assert response["Content-Type"] == "application/json"
    data = response.json()
    assert data == expected_data


def test_view_handler_caching(client):
    response = client.get("/stuff")
    assert response.status_code == 200
    check_data(response, {"slug": "stuff", "ext": None})
    assert "Cache-Control" in response
    assert "Expires" in response
    cache_control = sorted(response["Cache-Control"].split(", "))
    assert cache_control == ["max-age=5", "public"]
    assert "Vary" in response
    assert response["Vary"] == "Accept, Cookie"


def test_view_handler_caching_and_vary_on(client):
    response = client.get("/things")
    assert response.status_code == 200
    check_data(response, {"slug": "things"})
    assert "Cache-Control" in response
    assert "Expires" in response
    cache_control = sorted(response["Cache-Control"].split(", "))
    assert cache_control == ["max-age=10", "public"]
    assert "Vary" in response
    assert response["Vary"] == "Accept, Accept-Language, Cookie"


def test_view_handler_private_caching(client):
    response = client.get("/private")
    assert response.status_code == 200
    check_data(response, {"slug": "private"})
    assert "Cache-Control" in response
    assert "Expires" not in response
    assert response["Cache-Control"] == "private"
    assert "Vary" not in response
