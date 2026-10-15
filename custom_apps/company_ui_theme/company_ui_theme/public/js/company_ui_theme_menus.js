/*
 * Company UI Theme — hide upstream-product rows in the Desk Help and user menus.
 *
 * Frappe builds these menus from `frappe.boot.navbar_settings` (Navbar Settings) and already
 * skips rows whose `hidden` is set. boot.py sends the rows to hide in
 * `frappe.boot.company_ui_theme` (labels such as "Frappe School", "About", plus any row that
 * links to the upstream products' sites); this marks them hidden in the browser's copy of the
 * menu data before the menus are first built. Nothing is saved: the Navbar Settings record and
 * every other user's menus are unchanged.
 */
(function () {
	"use strict";

	const boot = window.frappe && window.frappe.boot;
	const navbar = boot && boot.navbar_settings;
	const rules = boot && boot.company_ui_theme;
	if (!navbar || !rules) return;

	const labels = new Set(rules.hide_help_items || []);
	const link = rules.framework_link ? new RegExp(rules.framework_link, "i") : null;

	for (const table of ["help_dropdown", "settings_dropdown"]) {
		for (const row of navbar[table] || []) {
			if (
				labels.has(row.item_label) ||
				(link && link.test(row.route || "")) ||
				/show_about/.test(row.action || "")
			) {
				row.hidden = 1;
			}
		}
	}
})();
