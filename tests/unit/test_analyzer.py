from followback.analyzer import analyze


def _followers(*names):
    return [{"string_list_data": [{"value": n}]} for n in names]


def _following(*names):
    return {"relationships_following": [{"title": n, "string_list_data": []} for n in names]}


def test_lista_quem_nao_segue_de_volta():
    result = analyze(_followers("ana"), _following("ana", "bia"))
    assert result["not_following_back"] == ["bia"]


def test_lista_fas_e_mutuos():
    result = analyze(_followers("ana", "caio"), _following("ana", "bia"))
    assert result["fans"] == ["caio"]
    assert result["mutuals"] == ["ana"]
