"""Unit tests for the Qulix white-label hooks (boot.py, website.py).

They replace `frappe` with a stub, so they need no site:

	python -m unittest company_ui_theme.tests.test_white_label
"""

import types
import unittest
from unittest import mock

from company_ui_theme import boot, website


class _Dict(dict):
	__getattr__ = dict.get


def fake_frappe(conf=None, roles=("Employee",), user="user@example.com"):
	return types.SimpleNamespace(
		conf=conf or {},
		get_roles=lambda: list(roles),
		session=types.SimpleNamespace(user=user),
	)


def app_data():
	return _Dict(
		app_data=[
			{
				"app_name": "frappe",
				"app_title": "Framework",
				"app_logo_url": "/f.svg",
				"on_apps_screen": True,
			},
			{"app_name": "erpnext", "app_title": "ERPNext", "app_logo_url": "/e.svg", "on_apps_screen": True},
			{"app_name": "hrms", "app_title": "Frappe HR", "app_logo_url": "/h.svg", "on_apps_screen": True},
		]
	)


def titles(bootinfo):
	return {a["app_name"]: a["app_title"] for a in bootinfo.app_data}


class TestBoot(unittest.TestCase):
	def test_default_relabels_only_hrms(self):
		with mock.patch.object(boot, "frappe", fake_frappe()):
			b = app_data()
			boot.extend_bootinfo(b)
		self.assertEqual(titles(b), {"frappe": "Framework", "erpnext": "ERPNext", "hrms": "Qulix"})
		# logos and tile visibility untouched without configuration
		self.assertEqual(b.app_data[2]["app_logo_url"], "/h.svg")
		self.assertTrue(all(a["on_apps_screen"] for a in b.app_data))

	def test_site_config_overrides_defaults(self):
		conf = {"company_ui_brand": {"product_name": "Other", "app_titles": {"erpnext": "Business"}}}
		with mock.patch.object(boot, "frappe", fake_frappe(conf)):
			b = app_data()
			boot.extend_bootinfo(b)
		self.assertEqual(titles(b), {"frappe": "Framework", "erpnext": "Business", "hrms": "Other"})
		self.assertIsNone(b.app_data[1]["app_logo_url"])

	def test_tile_roles_are_display_only(self):
		conf = {"company_ui_brand": {"app_tile_roles": {"erpnext": ["System Manager"]}}}
		with mock.patch.object(boot, "frappe", fake_frappe(conf)):
			b = app_data()
			boot.extend_bootinfo(b)
		self.assertFalse(b.app_data[1]["on_apps_screen"])
		with mock.patch.object(boot, "frappe", fake_frappe(conf, roles=("System Manager",))):
			b = app_data()
			boot.extend_bootinfo(b)
		self.assertTrue(b.app_data[1]["on_apps_screen"])

	def test_no_app_data_is_a_no_op(self):
		with mock.patch.object(boot, "frappe", fake_frappe()):
			b = _Dict()
			boot.extend_bootinfo(b)
		self.assertEqual(b, {})


class TestWebsiteContext(unittest.TestCase):
	def run_hook(self, app_name, conf=None):
		with mock.patch.object(boot, "frappe", fake_frappe(conf)):
			return website.update_website_context({"app_name": app_name})

	def test_replaces_framework_fallback(self):
		self.assertEqual(self.run_hook("Frappe"), {"app_name": "Qulix"})
		self.assertEqual(self.run_hook(""), {"app_name": "Qulix"})
		self.assertEqual(self.run_hook(None), {"app_name": "Qulix"})

	def test_keeps_a_site_configured_app_name(self):
		self.assertIsNone(self.run_hook("Acme HR"))

	def test_uses_site_override(self):
		conf = {"company_ui_brand": {"product_name": "Other"}}
		self.assertEqual(self.run_hook("Frappe", conf), {"app_name": "Other"})


class TestTranslations(unittest.TestCase):
	def test_en_csv_maps_product_strings(self):
		import csv
		from pathlib import Path

		path = Path(boot.__file__).parent / "translations" / "en.csv"
		with path.open(encoding="utf-8") as f:
			rows = dict(csv.reader(f))
		self.assertEqual(rows["Frappe HR"], "Qulix")
		self.assertEqual(rows["Get to know Frappe HR"], "Get to know Qulix")


if __name__ == "__main__":
	unittest.main()
