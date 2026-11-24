import re

from playwright.sync_api import Page, expect
BASE = "http://localhost:5000"


def login(page: Page, username, password="password"):
    page.goto(f"{BASE}/auth/login")
    page.fill('input[name="username"]', username)
    page.fill('input[name="password"]', password)
    page.click('button[type="submit"]')


def test_login_admin(page: Page):
    login(page, "test-admin")

    # Accesso riuscito: la barra in alto mostra l'utente e il link alla blocklist
    expect(page.locator("nav .user")).to_contain_text("test-admin")
    expect(page.locator("nav a", has_text="Blocklist")).to_be_visible()


def test_login_con_password_sbagliata(page: Page):
    login(page, "test-admin", "password-sbagliata")

    expect(page.locator(".error")).to_be_visible()


def test_dashboard_senza_login_porta_al_login(page: Page):
    page.goto(f"{BASE}/dashboard/")

    expect(page).to_have_url(re.compile(r"/auth/login"))


def test_analyst_non_vede_la_blocklist(page: Page):
    login(page, "test-analyst")

    expect(page.locator("nav .user")).to_contain_text("analyst")
    expect(page.locator("nav a", has_text="Blocklist")).to_have_count(0)

    page.goto(f"{BASE}/dashboard/blocklist")
    expect(page.locator("body")).to_contain_text("Forbidden")


def test_tentativo_sull_honeypot_compare_in_dashboard(page: Page):
    # 1) Un "attaccante" prova il finto login
    page.goto(f"{BASE}/wp-login.php")
    page.fill('input[name="username"]', "utente-ui-test")
    page.fill('input[name="password"]', "pw-ui-test")
    page.click('button[type="submit"]')
    expect(page.locator(".error")).to_contain_text("non validi")

    # 2) L'admin lo ritrova nella dashboard
    login(page, "test-admin")
    expect(page.locator("td", has_text="utente-ui-test").first).to_be_visible()