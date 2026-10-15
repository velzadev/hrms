"""Qulix relabelling of the Desk app switcher, apps screen, rail and sidebar header.

Frappe builds `bootinfo.app_data` from each app's `add_to_apps_screen` hook, which carries the
upstream product names and logos ("Frappe HR", "ERPNext", "Framework"). This rewrites only the
`app_title`, `app_logo_url` and `on_apps_screen` of those entries in the boot payload and
nothing else. Routes, docks, permissions and the apps themselves are untouched, and nothing is
written to the database. Other visible product-name strings (e.g. the HR onboarding title) are
relabelled through translations/en.csv.

The Qulix defaults below apply on every site this app is installed on. A site can override any
key through `company_ui_brand` in its own `site_config.json`. Example:

	"company_ui_brand": {
		"product_name": "<Product name>",
		"product_app": "hrms",
		"product_mark": "/files/<product-icon>.png",
		"app_titles": {"erpnext": "Business", "frappe": "Admin Tools"},
		"app_tile_roles": {"erpnext": ["System Manager", "Accounts Manager"]}
	}

`app_tile_roles` hides an app's tile from the apps screen and switcher for users without any of
the listed roles. It is display-only: the user's access to that app's pages is not changed.
"""

import frappe

# The HRMS product is presented as Qulix. ERPNext and Framework keep their own labels.
DEFAULT_BRAND = {
	"product_name": "Qulix",
	"product_app": "hrms",
}


def get_brand():
	"""The Qulix defaults, overridden key by key by the site's `company_ui_brand`."""
	return {**DEFAULT_BRAND, **(frappe.conf.get("company_ui_brand") or {})}


def extend_bootinfo(bootinfo):
	brand = get_brand()
	if not bootinfo.get("app_data"):
		return

	product_app = brand.get("product_app")
	app_titles = brand.get("app_titles") or {}
	app_tile_roles = brand.get("app_tile_roles") or {}
	user_roles = set(frappe.get_roles())

	for app in bootinfo.app_data:
		name = app.get("app_name")

		if name == product_app:
			if brand.get("product_name"):
				app["app_title"] = brand["product_name"]
			if brand.get("product_mark"):
				app["app_logo_url"] = brand["product_mark"]
		elif name in app_titles:
			app["app_title"] = app_titles[name]
			# No logo: the desk draws a neutral letter icon from the title instead.
			app["app_logo_url"] = None

		roles = app_tile_roles.get(name)
		if roles and frappe.session.user != "Administrator" and not user_roles.intersection(roles):
			app["on_apps_screen"] = False
