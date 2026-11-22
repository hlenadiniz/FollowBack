import json
import threading
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer

import pytest

from api.analyze import handler


@pytest.fixture
def post():
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    def send(body):
        raw = body if isinstance(body, bytes) else json.dumps(body).encode()
        connection = HTTPConnection("127.0.0.1", server.server_port)
        connection.request("POST", "/api/analyze", raw)
        response = connection.getresponse()
        payload = json.loads(response.read())
        headers = dict(response.getheaders())
        connection.close()
        return response.status, payload, headers

    yield send
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)


def _followers(*names):
    return [{"string_list_data": [{"value": name}]} for name in names]


def _following(*names):
    return {"relationships_following": [{"title": name} for name in names]}


def test_api_returns_the_three_lists_for_a_valid_request(post):
    status, payload, _ = post(
        {"followers": _followers("ana", "caio"), "following": _following("ana", "bia")}
    )

    assert status == 200
    assert payload == {
        "not_following_back": ["bia"],
        "fans": ["caio"],
        "mutuals": ["ana"],
    }


def test_api_merges_followers_split_across_several_files(post):
    status, payload, _ = post(
        {
            "followers_files": [_followers("ana"), _followers("bia")],
            "following": _following("ana", "bia", "caio"),
        }
    )

    assert status == 200
    assert payload["not_following_back"] == ["caio"]
    assert payload["mutuals"] == ["ana", "bia"]


def test_api_replies_with_json_and_disables_caching(post):
    _, _, headers = post({"followers": [], "following": {}})

    assert headers["Content-Type"] == "application/json; charset=utf-8"
    assert headers["Cache-Control"] == "no-store"


def test_api_rejects_request_without_following_file(post):
    status, payload, _ = post({"followers": _followers("ana")})

    assert status == 400
    assert "inválidos" in payload["error"]


def test_api_rejects_body_that_is_not_json(post):
    status, payload, _ = post(b"isto nao e json")

    assert status == 400
    assert payload["error"]


def test_api_rejects_request_without_followers_file(post):
    status, payload, _ = post({"following": _following("ana")})

    assert status == 400
    assert "inválidos" in payload["error"]


def test_api_rejects_empty_followers_files_list(post):
    status, payload, _ = post({"followers_files": [], "following": _following("ana")})

    assert status == 400
    assert "ao menos um arquivo" in payload["error"]


def test_api_accepts_csv_lists(post):
    status, payload, _ = post(
        {"followers": "username\nana\nbia", "following": "username\nana\ncaio"}
    )

    assert status == 200
    assert payload == {"not_following_back": ["caio"], "fans": ["bia"], "mutuals": ["ana"]}


def test_api_error_responses_are_also_json_without_cache(post):
    _, _, headers = post(b"{}")

    assert headers["Content-Type"] == "application/json; charset=utf-8"
    assert headers["Cache-Control"] == "no-store"


def test_api_reports_which_csv_username_is_invalid(post):
    status, payload, _ = post({"followers": "usuario\nana souza", "following": "usuario\nana"})

    assert status == 400
    assert "ana souza" in payload["error"]
