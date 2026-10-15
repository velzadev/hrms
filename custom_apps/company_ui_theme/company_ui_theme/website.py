"""Quicxly branding on server-rendered pages (login, Desk shell, other website pages).

Frappe and ERPNext fill these from Website Settings or their own defaults ("Frappe" as the app
name, the Frappe logo on the login page, the ERPNext favicon and loading splash). This
`update_website_context` hook runs after them and replaces each value only when the site has not
configured its own, so a site's Website / Navbar Settings always win. Nothing is written to the
database.
"""

from company_ui_theme.boot import get_brand, site_app_logo, site_setting

FRAMEWORK_DEFAULT_NAMES = {"", "Frappe"}


def update_website_context(context):
	brand = get_brand()
	values = {}

	if brand.get("product_name") and (context.get("app_name") or "") in FRAMEWORK_DEFAULT_NAMES:
		values["app_name"] = brand["product_name"]

	# Login and password pages (`logo`), every page's favicon, and the Desk loading splash.
	if brand.get("logo") and not site_app_logo():
		values["logo"] = brand["logo"]
	if brand.get("favicon") and not site_setting("Website Settings", "favicon"):
		values["favicon"] = brand["favicon"]
	if brand.get("splash") and not site_setting("Website Settings", "splash_image"):
		values["splash_image"] = brand["splash"]

	return values or None
