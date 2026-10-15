"""Qulix product name on server-rendered pages (login, Desk shell, other website pages).

Frappe shows Website Settings → App Name, then System Settings → App Name, then "Frappe" in the
browser title and on the login page. This `update_website_context` hook replaces only that last
fallback, so a site that has set its own App Name keeps it. Nothing is written to the database.
"""

from company_ui_theme.boot import get_brand

FRAMEWORK_DEFAULT_NAMES = {"", "Frappe"}


def update_website_context(context):
	product_name = get_brand().get("product_name")
	if product_name and (context.get("app_name") or "") in FRAMEWORK_DEFAULT_NAMES:
		return {"app_name": product_name}
