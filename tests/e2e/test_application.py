from playwright.sync_api import expect


def _upload(page, followers, following):
    follower_files = (
        followers.get("files", followers) if isinstance(followers, dict) else followers
    )
    page.locator("#followers-files").set_input_files(follower_files)
    page.locator("#following-json").set_input_files(following)
    page.get_by_role("button", name="Analisar meus arquivos").click()


def test_homepage_explains_json_uploads_and_privacy(page, app_url):
    page.goto(app_url)

    expect(page).to_have_title("FollowBack — descubra quem não segue você de volta")
    expect(page.get_by_role("heading", name="Quem não segue você de volta?")).to_be_visible()
    expect(page.get_by_text("Seus arquivos não ficam armazenados.")).to_be_visible()
    expect(page.locator('input[type="file"]')).to_have_count(2)
    expect(page.locator("#followers-files")).to_have_attribute("multiple", "")


def test_submit_without_files_shows_clear_validation_message(page, app_url):
    page.goto(app_url)
    page.get_by_role("button", name="Analisar meus arquivos").click()

    expect(page.get_by_role("status")).to_have_text(
        "Selecione os arquivos de seguidores e o arquivo following.json."
    )
    expect(page.locator("#results")).to_be_hidden()


def test_json_upload_shows_non_followers_and_other_lists(page, app_url):
    page.goto(app_url)
    _upload(
        page,
        {
            "name": "followers_1.json",
            "mimeType": "application/json",
            "buffer": b'[{"string_list_data":[{"value":"ana"}]}]',
        },
        {
            "name": "following.json",
            "mimeType": "application/json",
            "buffer": b'{"relationships_following":[{"title":"ana"},{"title":"bia"}]}',
        },
    )

    expect(page.locator("#not-following-count")).to_have_text("1")
    expect(page.locator("#not-following-list")).to_contain_text("@bia")
    expect(page.locator("#mutuals-list")).to_contain_text("@ana")
    expect(page.locator("#not-following-list a")).to_have_attribute(
        "href", "https://www.instagram.com/bia/"
    )


def test_split_followers_files_are_merged_before_comparison(page, app_url):
    page.goto(app_url)
    _upload(
        page,
        {
            "files": [
                {
                    "name": "followers_1.json",
                    "mimeType": "application/json",
                    "buffer": b'[{"string_list_data":[{"value":"ana"}]}]',
                },
                {
                    "name": "followers_2.json",
                    "mimeType": "application/json",
                    "buffer": b'[{"string_list_data":[{"value":"bia"}]}]',
                },
            ]
        },
        {
            "name": "following.json",
            "mimeType": "application/json",
            "buffer": b'{"relationships_following":[{"title":"ana"},{"title":"bia"},{"title":"caio"}]}',
        },
    )

    expect(page.locator("#not-following-count")).to_have_text("1")
    expect(page.locator("#not-following-list")).to_contain_text("@caio")
    expect(page.locator("#mutuals-count")).to_have_text("2")
    expect(page.get_by_role("status")).to_contain_text("1 perfil não segue")


def test_invalid_json_structure_shows_actionable_error(page, app_url):
    page.goto(app_url)
    _upload(
        page,
        {
            "name": "followers.json",
            "mimeType": "application/json",
            "buffer": b'[null]',
        },
        {
            "name": "following.json",
            "mimeType": "application/json",
            "buffer": b'{"relationships_following":[{"title":"bia"}]}',
        },
    )

    expect(page.get_by_role("status")).to_contain_text("Arquivos inválidos")
    expect(page.locator("#results")).to_be_hidden()


def test_invalid_json_is_reported_before_upload(page, app_url):
    page.goto(app_url)
    _upload(
        page,
        {
            "name": "followers.json",
            "mimeType": "application/json",
            "buffer": b"{not json}",
        },
        {
            "name": "following.json",
            "mimeType": "application/json",
            "buffer": b'{"relationships_following":[{"title":"bia"}]}',
        },
    )

    expect(page.get_by_role("status")).to_contain_text(
        "followers.json não contém um JSON válido"
    )


def test_plain_text_api_error_does_not_surface_json_parse_exception(page, app_url):
    page.route(
        "**/api/analyze",
        lambda route: route.fulfill(
            status=502,
            content_type="text/plain",
            body="An error occurred with this application.",
        ),
    )
    page.goto(app_url)
    _upload(
        page,
        {
            "name": "followers.json",
            "mimeType": "application/json",
            "buffer": b'[{"string_list_data":[{"value":"ana"}]}]',
        },
        {
            "name": "following.json",
            "mimeType": "application/json",
            "buffer": b'{"relationships_following":[{"title":"bia"}]}',
        },
    )

    expect(page.get_by_role("status")).to_contain_text(
        "O servidor não conseguiu processar a análise (HTTP 502)"
    )
    expect(page.get_by_role("status")).not_to_contain_text("Unexpected token")


def test_reset_clears_files_and_previous_results(page, app_url):
    page.goto(app_url)
    _upload(
        page,
        {
            "name": "followers.json",
            "mimeType": "application/json",
            "buffer": b'[{"string_list_data":[{"value":"ana"}]}]',
        },
        {
            "name": "following.json",
            "mimeType": "application/json",
            "buffer": b'{"relationships_following":[{"title":"bia"}]}',
        },
    )
    expect(page.locator("#results")).to_be_visible()
    page.get_by_role("button", name="Nova análise").click()

    expect(page.locator("#results")).to_be_hidden()
    expect(page.locator("#followers-files")).to_have_value("")
    expect(page.locator("#status")).to_be_empty()


def test_everyone_following_back_shows_empty_state_message(page, app_url):
    page.goto(app_url)
    _upload(
        page,
        {
            "name": "followers_1.json",
            "mimeType": "application/json",
            "buffer": b'[{"string_list_data":[{"value":"ana"}]}]',
        },
        {
            "name": "following.json",
            "mimeType": "application/json",
            "buffer": b'{"relationships_following":[{"title":"ana"}]}',
        },
    )

    expect(page.locator("#not-following-count")).to_have_text("0")
    expect(page.locator("#not-following-list")).to_have_text(
        "Boa! Todo mundo segue você de volta."
    )
    expect(page.get_by_role("status")).to_have_text(
        "Análise pronta: todos os perfis que você segue também seguem você."
    )


def test_selected_file_names_are_shown_on_upload_cards(page, app_url):
    page.goto(app_url)
    page.locator("#followers-files").set_input_files(
        [
            {"name": "followers_1.json", "mimeType": "application/json", "buffer": b"[]"},
            {"name": "followers_2.json", "mimeType": "application/json", "buffer": b"[]"},
        ]
    )
    page.locator("#following-json").set_input_files(
        {"name": "following.json", "mimeType": "application/json", "buffer": b"{}"}
    )

    expect(page.locator("#followers-name")).to_have_text("2 arquivos selecionados")
    expect(page.locator("#following-name")).to_have_text("following.json")


def test_upload_layout_fits_a_mobile_viewport(page, app_url):
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(app_url)

    expect(page.get_by_role("heading", name="Quem não segue você de volta?")).to_be_visible()
    assert page.locator("body").evaluate(
        "(element) => element.scrollWidth <= window.innerWidth"
    )
