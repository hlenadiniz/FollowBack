import pytest

from followback.analyzer import analyze, extract_followers, extract_following


def _followers(*names):
    return [{"string_list_data": [{"value": name}]} for name in names]


def _following(*names):
    return {"relationships_following": [{"title": name} for name in names]}


def test_extract_followers_from_instagram_list():
    assert extract_followers(_followers("ana", "bia")) == {"ana", "bia"}


def test_extract_followers_from_instagram_wrapper():
    assert extract_followers({"relationships_followers": _followers("ana")}) == {"ana"}


def test_extract_followers_combines_all_split_instagram_files():
    files = {
        "files": [
            _followers("ana", "bia"),
            _followers("caio", "ana"),
        ]
    }

    assert extract_followers(files) == {"ana", "bia", "caio"}


@pytest.mark.parametrize("files", [[], "followers.json"])
def test_extract_followers_rejects_invalid_split_files_collection(files):
    with pytest.raises(ValueError, match="ao menos um arquivo"):
        extract_followers({"files": files})


def test_extract_followers_ignores_empty_values():
    data = [{"string_list_data": [{"value": ""}, {}, {"value": "ana"}]}]
    assert extract_followers(data) == {"ana"}


def test_extract_followers_from_empty_list():
    assert extract_followers([]) == set()


def test_extract_followers_normalizes_case_and_at_sign():
    assert extract_followers(_followers("@Ana", "ANA")) == {"ana"}


def test_extract_followers_collects_multiple_entries_per_item():
    data = [{"string_list_data": [{"value": "ana"}, {"value": "bia"}]}]
    assert extract_followers(data) == {"ana", "bia"}


def test_extract_following_from_instagram_wrapper():
    assert extract_following(_following("ana", "bia")) == {"ana", "bia"}


def test_extract_following_from_instagram_list():
    assert extract_following([{"title": "ana"}]) == {"ana"}


def test_extract_following_ignores_empty_values():
    assert extract_following([{}, {"title": ""}, {"title": "bia"}]) == {"bia"}


def test_extract_following_from_empty_wrapper():
    assert extract_following({"relationships_following": []}) == set()


def test_extract_following_normalizes_case_and_at_sign():
    assert extract_following(_following("@Ana", "ANA")) == {"ana"}


@pytest.mark.parametrize(
    ("header", "expected"),
    [
        ("username", "ana"),
        ("user_name", "ana"),
        ("user name", "ana"),
        ("handle", "ana"),
        ("login", "ana"),
        ("usuario", "ana"),
        ("usuário", "ana"),
        ("nome de usuário", "ana"),
    ],
)
def test_csv_recognizes_username_headers(header, expected):
    assert extract_followers(f"{header}\n@Ana\n") == {expected}


@pytest.mark.parametrize(
    "csv_content",
    [
        "username,perfil\nana,Ana Souza\n",
        "perfil;username\nAna Souza;ana\n",
        "username\tperfil\nana\tAna Souza\n",
    ],
)
def test_csv_supports_common_delimiters_and_username_column(csv_content):
    assert extract_followers(csv_content) == {"ana"}


def test_csv_accepts_one_username_per_line_without_header():
    assert extract_followers("ana\nbia\n") == {"ana", "bia"}


def test_csv_ignores_utf8_bom():
    assert extract_followers("\ufeffusername\nana\n") == {"ana"}


def test_csv_ignores_blank_rows():
    assert extract_followers("username\n\nana\n  \n") == {"ana"}


def test_csv_removes_duplicates_and_normalizes_case():
    assert extract_followers("username\nAna\nana\n@ANA\n") == {"ana"}


def test_csv_allows_header_without_usernames():
    assert extract_followers("username\n") == set()


@pytest.mark.parametrize("csv_content", ["", " \n\t"])
def test_csv_rejects_empty_file(csv_content):
    with pytest.raises(ValueError, match="vazio"):
        extract_followers(csv_content)


@pytest.mark.parametrize("username", ["ana souza", "ana/bia", "muito" * 8])
def test_csv_rejects_invalid_username(username):
    with pytest.raises(ValueError, match="Username inválido"):
        extract_followers(f"username\n{username}\n")


@pytest.mark.parametrize(
    ("followers", "following", "key", "expected"),
    [
        (_followers("ana"), _following("ana", "bia"), "not_following_back", ["bia"]),
        (_followers("ana", "caio"), _following("ana", "bia"), "fans", ["caio"]),
        (_followers("ana", "caio"), _following("ana", "bia"), "mutuals", ["ana"]),
        ([], [], "not_following_back", []),
        ([], _following("bia"), "not_following_back", ["bia"]),
        (_followers("bia"), [], "fans", ["bia"]),
        (_followers("zoe", "ana"), _following("caio", "bia"), "fans", ["ana", "zoe"]),
        (_followers("ana"), _following("ANA"), "mutuals", ["ana"]),
    ],
)
def test_analyze_returns_expected_sorted_categories(followers, following, key, expected):
    assert analyze(followers, following)[key] == expected


def test_analyze_accepts_csv_for_both_lists():
    result = analyze("username\nana\nbia\n", "username\nana\ncaio\n")
    assert result == {
        "not_following_back": ["caio"],
        "fans": ["bia"],
        "mutuals": ["ana"],
    }


def test_analyze_always_returns_all_categories():
    assert analyze([], []) == {
        "not_following_back": [],
        "fans": [],
        "mutuals": [],
    }


def test_extract_followers_combines_json_and_csv_files():
    data = {"files": [[{"string_list_data": [{"value": "ana"}]}], "usuario\nbia"]}

    assert extract_followers(data) == {"ana", "bia"}


def test_analyze_treats_usernames_with_different_case_as_the_same_person():
    followers = [{"string_list_data": [{"value": "Ana"}]}]
    following = {"relationships_following": [{"title": "ana"}]}

    result = analyze(followers, following)

    assert result["mutuals"] == ["ana"]
    assert result["not_following_back"] == []


def test_analyze_with_nobody_followed_lists_everyone_as_follower_only():
    followers = [{"string_list_data": [{"value": "ana"}]}]

    result = analyze(followers, {"relationships_following": []})

    assert result == {"not_following_back": [], "fans": ["ana"], "mutuals": []}

