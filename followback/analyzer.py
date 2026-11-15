"""Compara seguidores e seguindo a partir dos formatos do Instagram e de CSVs."""

import csv
import io
import re

_USERNAME_HEADERS = {
    "handle",
    "login",
    "user",
    "user name",
    "username",
    "user_name",
    "usuario",
    "usuário",
    "nome de usuario",
    "nome de usuário",
}
_USERNAME_PATTERN = re.compile(r"[A-Za-z0-9._]{1,30}\Z")


def _normalize_username(value):
    username = value.strip().removeprefix("@")
    if not _USERNAME_PATTERN.fullmatch(username):
        raise ValueError(f"Username inválido no CSV: {value.strip()!r}")
    return username.lower()


def _extract_csv_usernames(data):
    if not data.strip():
        raise ValueError("O arquivo CSV está vazio.")

    sample = data[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
    except csv.Error:
        dialect = csv.excel

    rows = list(csv.reader(io.StringIO(data.lstrip("\ufeff")), dialect))
    rows = [row for row in rows if any(cell.strip() for cell in row)]
    if not rows:
        raise ValueError("O arquivo CSV está vazio.")

    headers = [cell.strip().lower() for cell in rows[0]]
    username_column = next(
        (index for index, value in enumerate(headers) if value in _USERNAME_HEADERS),
        None,
    )
    if username_column is None:
        username_column = 0
    else:
        rows = rows[1:]

    usernames = set()
    for row in rows:
        if username_column < len(row) and row[username_column].strip():
            usernames.add(_normalize_username(row[username_column]))
    return usernames


def extract_followers(data):
    """Extrai usernames de um JSON de seguidores ou de vários arquivos do Instagram."""
    if isinstance(data, str):
        return _extract_csv_usernames(data)
    if isinstance(data, dict) and "files" in data:
        files = data["files"]
        if not isinstance(files, list) or not files:
            raise ValueError("Selecione ao menos um arquivo de seguidores.")
        return set().union(*(extract_followers(file_data) for file_data in files))
    items = data if isinstance(data, list) else data.get("relationships_followers", [])
    return {
        entry["value"].strip().removeprefix("@").lower()
        for item in items
        for entry in item.get("string_list_data", [])
        if entry.get("value")
    }


def extract_following(data):
    """Extrai usernames de following.json ou de um CSV de usernames."""
    if isinstance(data, str):
        return _extract_csv_usernames(data)
    items = data.get("relationships_following", []) if isinstance(data, dict) else data
    return {
        item["title"].strip().removeprefix("@").lower()
        for item in items
        if item.get("title")
    }


def analyze(followers_json, following_json):
    followers = extract_followers(followers_json)
    following = extract_following(following_json)
    return {
        "not_following_back": sorted(following - followers),
        "fans": sorted(followers - following),
        "mutuals": sorted(followers & following),
    }
