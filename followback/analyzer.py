"""Lógica pura do FollowBack: compara seguidores e seguindo com teoria de conjuntos."""


def extract_followers(data):
    """Extrai usernames de followers.json (lista no topo; username em `value`)."""
    items = data if isinstance(data, list) else data.get("relationships_followers", [])
    return {
        entry["value"]
        for item in items
        for entry in item.get("string_list_data", [])
        if entry.get("value")
    }


def extract_following(data):
    """Extrai usernames de following.json (objeto com `relationships_following`; username em `title`)."""
    items = data.get("relationships_following", []) if isinstance(data, dict) else data
    return {item["title"] for item in items if item.get("title")}


def analyze(followers_json, following_json):
    followers = extract_followers(followers_json)
    following = extract_following(following_json)
    return {
        "not_following_back": sorted(following - followers),
        "fans": sorted(followers - following),
        "mutuals": sorted(followers & following),
    }
