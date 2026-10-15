"""Unit tests for the Quicxly white-label hooks (boot.py, website.py) and assets.

They replace `frappe` with a stub, so they need no site:

	python -m unittest company_ui_theme.tests.test_white_label
"""

import csv
import re
import types
import unittest
from pathlib import Path
from unittest import mock

from company_ui_theme import boot, website

IMAGES = boot.IMAGES
PUBLIC = Path(boot.__file__).parent / "public"


class _Dict(dict):
	__getattr__ = dict.get

	def __setattr__(self, key, value):
		self[key] = value


def fake_frappe(conf=None, roles=("Employee",), user="user@example.com", settings=None):
	settings = settings or {}
	return types.SimpleNamespace(
		conf=conf or {},
		get_roles=lambda: list(roles),
		session=types.SimpleNamespace(user=user),
		db=types.SimpleNamespace(get_single_value=lambda doctype, field: settings.get((doctype, field))),
	)


def boot_payload():
	return _Dict(
		app_logo_url="/assets/frappe/images/frappe-framework-logo.svg",
		app_data=[
			{
				"app_name": "frappe",
				"app_title": "Framework",
				"app_logo_url": "/f.svg",
				"on_apps_screen": True,
			},
			{"app_name": "erpnext", "app_title": "ERPNext", "app_logo_url": "/e.svg", "on_apps_screen": True},
			{"app_name": "hrms", "app_title": "Frappe HR", "app_logo_url": "/h.svg", "on_apps_screen": True},
		],
	)


def run_boot(**kwargs):
	with mock.patch.object(boot, "frappe", fake_frappe(**kwargs)):
		b = boot_payload()
		boot.extend_bootinfo(b)
	return b


def apps(b):
	return {a["app_name"]: (a["app_title"], a["app_logo_url"]) for a in b.app_data}


class TestBoot(unittest.TestCase):
	def test_defaults(self):
		b = run_boot()
		self.assertEqual(
			apps(b),
			{
				"frappe": ("Administration", None),
				"erpnext": ("Business", None),
				"hrms": ("Quicxly", f"{IMAGES}/quicxly-mark-512.png"),
			},
		)
		self.assertEqual(b.app_logo_url, f"{IMAGES}/quicxly-mark-512.png")
		self.assertTrue(all(a["on_apps_screen"] for a in b.app_data))

	def test_site_logo_wins_for_launcher_logo(self):
		b = run_boot(settings={("Navbar Settings", "app_logo"): "/files/site-logo.png"})
		self.assertEqual(b.app_logo_url, "/assets/frappe/images/frappe-framework-logo.svg")

	def test_site_config_overrides_defaults(self):
		conf = {"company_ui_brand": {"product_name": "Other", "app_titles": {"erpnext": "Shop"}}}
		b = run_boot(conf=conf)
		self.assertEqual(apps(b)["hrms"][0], "Other")
		self.assertEqual(apps(b)["erpnext"], ("Shop", None))
		# app_titles replaced as a whole: Framework keeps its own label and logo
		self.assertEqual(apps(b)["frappe"], ("Framework", "/f.svg"))

	def test_tile_roles_are_display_only(self):
		conf = {"company_ui_brand": {"app_tile_roles": {"erpnext": ["System Manager"]}}}
		self.assertFalse(run_boot(conf=conf).app_data[1]["on_apps_screen"])
		self.assertTrue(run_boot(conf=conf, roles=("System Manager",)).app_data[1]["on_apps_screen"])

	def test_no_app_data_only_sets_launcher_logo_and_menu_rules(self):
		with mock.patch.object(boot, "frappe", fake_frappe()):
			b = _Dict()
			boot.extend_bootinfo(b)
		self.assertEqual(set(b), {"app_logo_url", "company_ui_theme"})
		self.assertEqual(b.app_logo_url, f"{IMAGES}/quicxly-mark-512.png")

	def test_menu_rules_sent_to_client(self):
		rules = run_boot().company_ui_theme
		self.assertEqual(
			set(rules["hide_help_items"]),
			{"Documentation", "User Forum", "Frappe School", "Report an Issue", "About", "Frappe Support"},
		)
		link = re.compile(rules["framework_link"], re.IGNORECASE)
		for url in (
			"https://frappe.io/support",
			"https://docs.erpnext.com/",
			"https://github.com/frappe/erpnext/issues",
		):
			self.assertTrue(link.search(url), url)
		self.assertFalse(link.search("/desk/system-health-report"))


class TestWebsiteContext(unittest.TestCase):
	def run_hook(self, context, **kwargs):
		with mock.patch.object(boot, "frappe", fake_frappe(**kwargs)):
			return website.update_website_context(context) or {}

	def test_defaults_on_unconfigured_site(self):
		v = self.run_hook({"app_name": "Frappe"})
		self.assertEqual(v["app_name"], "Quicxly")
		self.assertEqual(v["logo"], f"{IMAGES}/quicxly-logo-light.png")
		self.assertEqual(v["favicon"], f"{IMAGES}/quicxly-mark-64.png")
		self.assertEqual(v["splash_image"], f"{IMAGES}/quicxly-mark-512.png")

	def test_keeps_site_configured_values(self):
		settings = {
			("Website Settings", "app_logo"): "/files/a.png",
			("Website Settings", "favicon"): "/files/f.png",
			("Website Settings", "splash_image"): "/files/s.png",
		}
		self.assertEqual(self.run_hook({"app_name": "Acme HR"}, settings=settings), {})

	def test_app_name_fallbacks(self):
		for name in ("Frappe", "", None):
			self.assertEqual(self.run_hook({"app_name": name})["app_name"], "Quicxly")

	def test_site_override(self):
		conf = {"company_ui_brand": {"product_name": "Other"}}
		self.assertEqual(self.run_hook({"app_name": "Frappe"}, conf=conf)["app_name"], "Other")


class TestAssetsAndTranslations(unittest.TestCase):
	def test_hook_urls_carry_content_hash(self):
		import hashlib

		from company_ui_theme import hooks

		urls = hooks.app_include_css + hooks.app_include_js + hooks.web_include_css
		self.assertEqual(len(urls), 4)
		for url in urls:
			path, _, version = url.partition("?v=")
			data = (PUBLIC / path.removeprefix("/assets/company_ui_theme/")).read_bytes()
			self.assertEqual(version, hashlib.sha1(data).hexdigest()[:10], url)

	def test_default_assets_exist(self):
		for key in ("product_mark", "logo", "splash", "favicon"):
			url = boot.DEFAULT_BRAND[key]
			path = PUBLIC / url.removeprefix("/assets/company_ui_theme/")
			self.assertTrue(path.is_file(), f"{key}: {url} has no file at {path}")

	def test_en_csv_maps_product_strings(self):
		path = Path(boot.__file__).parent / "translations" / "en.csv"
		with path.open(encoding="utf-8") as f:
			rows = dict(csv.reader(f))
		self.assertEqual(rows["Frappe HR"], "Quicxly")
		self.assertEqual(rows["Get to know Frappe HR"], "Get to know Quicxly")
		self.assertEqual(rows["ERPNext Settings"], "Business Settings")
		self.assertEqual(rows["Get to know ERPNext"], "Get to know Business")


if __name__ == "__main__":
	unittest.main()
