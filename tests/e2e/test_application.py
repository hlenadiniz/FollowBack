from playwright.sync_api import expect


def _upload(page, followers, following):
    page.locator("#followers-file").set_input_files(followers)
    page.locator("#following-file").set_input_files(following)
    page.get_by_role("button", name="Analisar meus arquivos").click()


def test_homepage_explains_csv_uploads_and_privacy(page, app_url):
    page.goto(app_url)

    expect(page).to_have_title("FollowBack — descubra quem não segue você de volta")
    expect(page.get_by_role("heading", name="Quem não segue você de volta?")).to_be_visible()
    expect(page.get_by_text("Seus arquivos não ficam armazenados.")).to_be_visible()
    expect(page.locator('input[type="file"]')).to_have_count(2)


def test_submit_without_files_shows_clear_validation_message(page, app_url):
    page.goto(app_url)
    page.get_by_role("button", name="Analisar meus arquivos").click()

    expect(page.get_by_role("status")).to_have_text(
        "Selecione os dois arquivos para continuar."
    )
    expect(page.locator("#results")).to_be_hidden()


def test_csv_upload_shows_non_followers_and_other_lists(page, app_url):
    page.goto(app_url)
    _upload(
        page,
        {
            "name": "followers.csv",
            "mimeType": "text/csv",
            "buffer": b"username\nana\n",
        },
        {
            "name": "following.csv",
            "mimeType": "text/csv",
            "buffer": b"username\nana\nbia\n",
        },
    )

    expect(page.locator("#not-following-count")).to_have_text("1")
    expect(page.locator("#not-following-list")).to_contain_text("@bia")
    expect(page.locator("#mutuals-list")).to_contain_text("@ana")
    expect(page.locator("#not-following-list a")).to_have_attribute(
        "href", "https://www.instagram.com/bia/"
    )


def test_instagram_json_upload_remains_supported(page, app_url):
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
            "buffer": b'{"relationships_following":[{"title":"bia"}]}',
        },
    )

    expect(page.locator("#not-following-count")).to_have_text("1")
    expect(page.locator("#not-following-list")).to_contain_text("@bia")
    expect(page.get_by_role("status")).to_contain_text("1 perfil não segue")


def test_invalid_csv_shows_actionable_error(page, app_url):
    page.goto(app_url)
    _upload(
        page,
        {
            "name": "followers.csv",
            "mimeType": "text/csv",
            "buffer": b"username\nana souza\n",
        },
        {
            "name": "following.csv",
            "mimeType": "text/csv",
            "buffer": b"username\nbia\n",
        },
    )

    expect(page.get_by_role("status")).to_contain_text("Username inválido")
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
            "name": "following.csv",
            "mimeType": "text/csv",
            "buffer": b"username\nbia\n",
        },
    )

    expect(page.get_by_role("status")).to_contain_text(
        "followers.json não contém um JSON válido"
    )


def test_reset_clears_files_and_previous_results(page, app_url):
    page.goto(app_url)
    _upload(
        page,
        {
            "name": "followers.csv",
            "mimeType": "text/csv",
            "buffer": b"username\nana\n",
        },
        {
            "name": "following.csv",
            "mimeType": "text/csv",
            "buffer": b"username\nbia\n",
        },
    )
    expect(page.locator("#results")).to_be_visible()
    page.get_by_role("button", name="Nova análise").click()

    expect(page.locator("#results")).to_be_hidden()
    expect(page.locator("#followers-file")).to_have_value("")
    expect(page.locator("#status")).to_be_empty()


def test_upload_layout_fits_a_mobile_viewport(page, app_url):
    page.set_viewport_size({"width": 390, "height": 844})
    page.goto(app_url)

    expect(page.get_by_role("heading", name="Quem não segue você de volta?")).to_be_visible()
    assert page.locator("body").evaluate(
        "(element) => element.scrollWidth <= window.innerWidth"
    )
