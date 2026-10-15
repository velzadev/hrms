/*
 * Company UI Theme — Desk light/dark theme controller (Frappe v16).
 *
 * Works *with* Frappe's own theme mechanism instead of replacing it:
 *   <html data-theme-mode="light|dark|automatic">  — the user's choice
 *   <html data-theme="light|dark">                — what is shown, resolved by
 *                                                    frappe.ui.set_theme()
 * Frappe (desk.js) already observes data-theme-mode and calls set_theme(), and
 * already follows the OS while the mode is "automatic". This file only:
 *   - restores this browser's saved preference from localStorage; when
 *     nothing is saved it keeps the mode Frappe rendered from the user's own
 *     Desk theme setting (desk.html), so existing preferences are respected,
 *   - adds one toggle button to each page header (.page-head
 *     .standard-items-section), on Frappe's "page-change" event,
 *   - keeps localStorage in sync if the user changes the theme through
 *     Frappe's own "Switch Theme" dialog (Ctrl+Shift+G / user settings).
 *
 * No globals are created, no timers or polling are used, and only one
 * MutationObserver is registered (on <html> attributes, guarded against
 * double loading).
 */
(function () {
	"use strict";

	const STORAGE_KEY = "company_ui_theme.desk_theme";
	const EXPLICIT_MODES = ["light", "dark"];
	const TOGGLE_CLASS = "ui-theme-toggle";
	const root = document.documentElement;

	// The script can be included twice (e.g. a stale asset plus a fresh one); run once.
	if (root.hasAttribute("data-ui-theme")) return;
	root.setAttribute("data-ui-theme", "");

	const translate = (text) => (typeof window.__ === "function" ? window.__(text) : text);

	const storage = {
		get() {
			try {
				const value = window.localStorage.getItem(STORAGE_KEY);
				return EXPLICIT_MODES.includes(value) ? value : null;
			} catch (e) {
				return null; // storage blocked (privacy mode, policy); keep Frappe's setting
			}
		},
		set(mode) {
			try {
				if (EXPLICIT_MODES.includes(mode)) {
					window.localStorage.setItem(STORAGE_KEY, mode);
				} else {
					window.localStorage.removeItem(STORAGE_KEY);
				}
			} catch (e) {
				// not persisted; the choice still applies until reload
			}
		},
	};

	// The mode this controller last wrote, so the observer can tell its own
	// changes apart from ones made by Frappe's theme switcher.
	let expected_mode = null;

	function current_theme() {
		return root.getAttribute("data-theme") === "dark" ? "dark" : "light";
	}

	function apply_mode(mode) {
		expected_mode = mode;
		if (root.getAttribute("data-theme-mode") !== mode) {
			root.setAttribute("data-theme-mode", mode);
		}
		// Frappe's own observer does this once the desk has booted; before that
		// (first paint) resolve it here so there is no flash of the wrong theme.
		if (window.frappe && frappe.ui && typeof frappe.ui.set_theme === "function") {
			frappe.ui.set_theme();
		} else if (mode !== "automatic") {
			root.setAttribute("data-theme", mode);
		}
	}

	function sync_toggles() {
		const is_dark = current_theme() === "dark";
		const label = is_dark
			? translate("Switch to light theme")
			: translate("Switch to dark theme");
		document.querySelectorAll("." + TOGGLE_CLASS).forEach((button) => {
			button.setAttribute("aria-label", label);
			button.setAttribute("title", label);
			button.setAttribute("aria-pressed", String(is_dark));
		});
	}

	function toggle_theme() {
		const next = current_theme() === "dark" ? "light" : "dark";
		storage.set(next);
		apply_mode(next);
		sync_toggles();
	}

	function icon(name) {
		if (window.frappe && frappe.utils && typeof frappe.utils.icon === "function") {
			return frappe.utils.icon(name, "sm");
		}
		return "";
	}

	function make_toggle() {
		const button = document.createElement("button");
		button.type = "button";
		// Espresso ghost icon-button: same look and focus behaviour as Frappe's own.
		button.className = "es-button " + TOGGLE_CLASS;
		button.setAttribute("data-variant", "ghost");
		button.setAttribute("data-icon-button", "true");
		// CSS shows the moon in light mode and the sun in dark mode.
		button.innerHTML =
			`<span class="ui-theme-icon-moon" aria-hidden="true">${icon("moon")}</span>` +
			`<span class="ui-theme-icon-sun" aria-hidden="true">${icon("sun")}</span>`;
		button.addEventListener("click", toggle_theme);
		return button;
	}

	// Add the toggle to the header of the page being shown, once per page.
	// Frappe keeps each page's DOM after it is first built, so this is a no-op
	// on revisits.
	function ensure_toggle(page) {
		const head = page && page.querySelector && page.querySelector(".page-head");
		const section = head && head.querySelector(".standard-items-section");
		if (!section || section.querySelector("." + TOGGLE_CLASS)) return;

		const actions = section.querySelector(":scope > .page-actions");
		section.insertBefore(make_toggle(), actions || null);
		sync_toggles();
	}

	function on_page_change(_event, page) {
		const target = page || (window.frappe && frappe.container && frappe.container.page);
		ensure_toggle(target);
		// Some pages finish building their header in "show" handlers that run
		// right after page-change; check once more on the next frame.
		window.requestAnimationFrame(() => ensure_toggle(target));
	}

	function watch_theme_attributes() {
		const observer = new MutationObserver(() => {
			const mode = root.getAttribute("data-theme-mode");
			if (mode && mode !== expected_mode) {
				// Changed through Frappe's Switch Theme dialog: adopt it, so the
				// two controls never disagree after a reload.
				expected_mode = mode;
				storage.set(mode); // "automatic" clears the saved preference
			}
			sync_toggles();
		});
		observer.observe(root, {
			attributes: true,
			attributeFilter: ["data-theme-mode", "data-theme"],
		});
	}

	// 1. Apply this browser's saved preference immediately (this runs before the
	//    desk boots). Without one, keep the user's Desk theme setting as rendered.
	const saved_mode = storage.get();
	if (saved_mode) {
		apply_mode(saved_mode);
	} else {
		expected_mode = root.getAttribute("data-theme-mode");
	}

	// 2. Keep toggles and storage in step with any theme change.
	watch_theme_attributes();

	// 3. Insert the toggle on every route change (Frappe triggers this via jQuery).
	if (window.jQuery) {
		window.jQuery(document).on("page-change.company_ui_theme", on_page_change);
	}
})();
