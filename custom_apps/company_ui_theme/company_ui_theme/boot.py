"""Quicxly relabelling of the Desk apps screen, app switcher, rail and sidebar header.

Frappe builds `bootinfo.app_data` from each app's `add_to_apps_screen` hook, which carries the
upstream product names and logos ("Frappe HR", "ERPNext", "Framework"). This rewrites only the
`app_title`, `app_logo_url` and `on_apps_screen` of those entries, and the launcher's own logo
(`bootinfo.app_logo_url`), in the boot payload and nothing else. Routes, docks, permissions and
the apps themselves are untouched, and nothing is written to the database. Other visible
product-name strings (e.g. the HR onboarding title) are relabelled through translations/en.csv,
and the login logo, favicon and loading splash are set in website.py.

The Quicxly defaults below apply on every site this app is installed on. A site can override any
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

Logos configured on the site itself (Website Settings / Navbar Settings) always win over these
defaults.
"""

import re

import frappe

IMAGES = "/assets/company_ui_theme/images"

# Help-menu rows that lead to the upstream products' sites or show their About dialog.
FRAMEWORK_LINK = re.compile(r"frappe\.io|erpnext\.com|github\.com/frappe", re.IGNORECASE)

# The HRMS product is presented as Quicxly. ERPNext and Framework stay installed and reachable,
# but under neutral labels and with Frappe's letter icon instead of their product logos.
DEFAULT_BRAND = {
	"product_name": "Quicxly",
	"product_app": "hrms",
	"app_titles": {"erpnext": "Business", "frappe": "Administration"},
	# Temporary assets cut from the supplied JPEG; see public/images/README.md.
	"product_mark": f"{IMAGES}/quicxly-mark-512.png",
	"logo": f"{IMAGES}/quicxly-logo-light.png",
	"splash": f"{IMAGES}/quicxly-mark-512.png",
	"favicon": f"{IMAGES}/quicxly-mark-64.png",
	# Help-menu rows hidden from users (display only; Navbar Settings itself is not changed).
	# Any row linking to the upstream products' sites is hidden as well.
	"hide_help_items": [
		"Documentation",
		"User Forum",
		"Frappe School",
		"Report an Issue",
		"About",
		"Frappe Support",
	],
}


def get_brand():
	"""The Quicxly defaults, overridden key by key by the site's `company_ui_brand`."""
	return {**DEFAULT_BRAND, **(frappe.conf.get("company_ui_brand") or {})}


def site_setting(doctype, fieldname):
	"""A branding value the site has configured itself (Website / Navbar Settings), if any."""
	value = frappe.db.get_single_value(doctype, fieldname)
	return value if value and value != "attach_files:" else None


def site_app_logo():
	return site_setting("Website Settings", "app_logo") or site_setting("Navbar Settings", "app_logo")


def extend_bootinfo(bootinfo):
	brand = get_brand()

	# Frappe sets `bootinfo.navbar_settings` after this hook runs, so the Help/user-menu rows to
	# hide are passed to the client, where company_ui_theme_menus.js marks them hidden in its
	# copy of the menu data. Display only: the Navbar Settings record is not changed.
	bootinfo.company_ui_theme = {
		"hide_help_items": list(brand.get("hide_help_items") or []),
		"framework_link": FRAMEWORK_LINK.pattern,
	}

	# The logo at the top of the apps screen (Frappe's own logo unless the site set one).
	if brand.get("product_mark") and not site_app_logo():
		bootinfo.app_logo_url = brand["product_mark"]

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
