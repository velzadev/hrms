"""Apply a site's white-label settings from its `company_ui_brand` site config.

Run explicitly, per site (it is not an install hook, so it never touches other sites):

	bench --site <site> execute company_ui_theme.branding.apply

It only writes branding fields: Website Settings (app name, logo, splash, favicon, footer
text), System Settings (app name, standard email footer), the visibility of the listed
Help-menu items in Navbar Settings, and English Translation records for the listed strings.
It is idempotent, and prints each value it changes with its previous value.
"""

import frappe

WEBSITE_FIELDS = {
	"app_name": "product_name",
	"app_logo": "logo",
	"splash_image": "splash",
	"favicon": "favicon",
	"footer_powered": "footer_text",
}


def apply():
	brand = frappe.conf.get("company_ui_brand")
	if not brand:
		frappe.throw("This site has no company_ui_brand key in site_config.json")

	website = frappe.get_single("Website Settings")
	for field, key in WEBSITE_FIELDS.items():
		_set(website, field, brand.get(key))
	website.save()

	system = frappe.get_single("System Settings")
	_set(system, "app_name", brand.get("product_name"))
	if "disable_standard_email_footer" in brand:
		_set(system, "disable_standard_email_footer", int(brand["disable_standard_email_footer"]))
	system.save()

	hide = set(brand.get("hide_help_items") or [])
	if hide:
		navbar = frappe.get_single("Navbar Settings")
		for item in navbar.help_dropdown:
			if item.item_label in hide and not item.hidden:
				print(f"Navbar Settings.help_dropdown[{item.item_label}].hidden: 0 -> 1")
				item.hidden = 1
		navbar.save()

	for source, target in (brand.get("translations") or {}).items():
		name = frappe.db.get_value("Translation", {"language": "en", "source_text": source})
		if name:
			doc = frappe.get_doc("Translation", name)
			if doc.translated_text == target:
				continue
			print(f"Translation[{source}]: {doc.translated_text!r} -> {target!r}")
			doc.translated_text = target
			doc.save()
		else:
			print(f"Translation[{source}]: (new) -> {target!r}")
			frappe.get_doc(
				{"doctype": "Translation", "language": "en", "source_text": source, "translated_text": target}
			).insert()

	frappe.db.commit()
	frappe.clear_cache()


def _set(doc, field, value):
	if value is None or doc.get(field) == value:
		return
	print(f"{doc.doctype}.{field}: {doc.get(field)!r} -> {value!r}")
	doc.set(field, value)
