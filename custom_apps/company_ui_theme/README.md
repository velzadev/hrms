## Company UI Theme

A reusable, brand-neutral Desk UI theme for Frappe HRMS v16 (Frappe v16, ERPNext v16, HRMS v16).

It is a pure UI layer: no DocTypes, no patches, no database changes, and no Frappe, ERPNext or
HRMS files are modified. It adds:

- **Dashboard styling** for Desk (workspaces, cards, widgets, dialogs, menus, child tables and
  report headers): rounded corners, 1px borders, soft shadows in light mode, flat cards in dark
  mode. All colours are Frappe's own theme variables, so the light and dark themes stay Frappe's.
- **A light/dark toggle** in every page header, kept in sync with Frappe's own theme switcher.
- **Optional, per-site relabelling** of the Desk app switcher (off unless configured), and an
  optional script that writes per-site branding settings. Neither ships any branding.

The app is kept in the `velzadev/hrms` repository under `custom_apps/company_ui_theme/`, separate
from the `hrms` Python package. It is a normal Frappe app with its own `pyproject.toml` and
`hooks.py`; it is just not at the root of its own Git repository, so it is linked into the bench
instead of being fetched with `bench get-app`.

### Requirements

- A Frappe v16 bench with Frappe, ERPNext and HRMS v16 (Python 3.14, as for Frappe v16)
- HRMS fetched from `https://github.com/velzadev/hrms` (branch `version-16`), which contains
  this folder

### Installation

Run from the bench directory (the one containing `apps/`, `sites/` and `env/`):

```bash
# 1. Get HRMS from this repository, if the bench does not have it yet
bench get-app https://github.com/velzadev/hrms --branch version-16

# 2. Link the theme app into apps/ (the target is relative to apps/)
ln -s hrms/custom_apps/company_ui_theme apps/company_ui_theme

# 3. Install it into the bench's Python environment
./env/bin/python -m pip install -e apps/company_ui_theme
#    (uv-based benches without pip: uv pip install --python env/bin/python -e apps/company_ui_theme)

# 4. Register it with the bench (the leading newline matters: bench writes apps.txt
#    without a trailing newline; Frappe ignores the blank line)
grep -qx company_ui_theme sites/apps.txt || printf '\ncompany_ui_theme\n' >> sites/apps.txt

# 5. Build its assets and install it on the site
bench build --app company_ui_theme
bench --site <your-site> install-app company_ui_theme
bench --site <your-site> clear-cache
```

Then hard-refresh Desk (Ctrl+Shift+R). The theme is active on every site the app is installed on.

Notes:

- Because `apps/company_ui_theme` is a symlink into the HRMS checkout, `git pull` in
  `apps/hrms` (or `bench update`) updates the theme too. `bench update` skips the link itself,
  as it is not a Git repository of its own.
- If you prefer a plain copy over a link, use `cp -r apps/hrms/custom_apps/company_ui_theme apps/`
  in step 2. You then have to re-copy it after updating HRMS.
- Do not place the folder at the root of the HRMS repository: the `hrms` editable install puts
  that root on `sys.path`, where it would shadow the installed app.

### Building and editing

The CSS and JS are plain (non-`.bundle`) files served from `/assets/company_ui_theme/`:

| File | Purpose |
| --- | --- |
| `company_ui_theme/public/css/company_ui_theme.css` | Shape and elevation tokens, component rules, toggle styles |
| `company_ui_theme/public/js/company_ui_theme.js` | Theme controller: saved preference, header toggle, sync with Frappe's switcher |
| `company_ui_theme/hooks.py` | Includes both files on Desk (`app_include_css` / `app_include_js`), registers `boot.py` |
| `company_ui_theme/boot.py` | Optional app-switcher relabelling (see below) |
| `company_ui_theme/branding.py` | Optional per-site branding script (see below) |

While `bench start` is running, a hard refresh is enough after editing them. Run
`bench build --app company_ui_theme` after adding new files or on a fresh bench. Desk includes
these files without a version query, so after deploying a change run `bench clear-cache` and ask
users to hard-refresh.

To restyle, change only the `--ui-theme-*` tokens at the top of the CSS (radii and shadows). For
colours, use Frappe's variables (`var(--primary-color)`, `var(--text-color)`, `var(--text-muted)`,
`var(--border-color)`, `var(--card-bg)`, `var(--fg-color)`) instead of hard-coded values, and test
both themes.

### How the theme toggle works

- Frappe already supports themes: `<html data-theme-mode>` holds the choice (`light` / `dark` /
  `automatic`), and `frappe.ui.set_theme()` resolves it into `<html data-theme>`. The controller
  only sets `data-theme-mode`, so Frappe's own components and charts stay consistent.
- **Initial value:** this browser's saved choice in `localStorage["company_ui_theme.desk_theme"]`.
  If there is none, the user's own Desk theme setting (as rendered by Frappe) is kept unchanged.
- **Toggle:** an icon button (moon in light mode, sun in dark mode) is added to each page header
  (`.page-head .standard-items-section`, before the page actions) on Frappe's `page-change` event.
  It is a native `<button>` with an `aria-label`, `aria-pressed` and Frappe's ghost icon-button
  styling. Clicking switches the theme instantly and saves the choice for this browser.
- **Frappe's own switcher** (Ctrl+Shift+G, or the user menu) still works and saves the user's
  setting on the server as usual; a MutationObserver adopts its choice into localStorage, and
  choosing "Automatic" there clears the saved browser choice.
- The header toggle does not write to the server, so a toggle choice is per browser.
- Blocked `localStorage` (private mode, policy) is handled; the theme still switches for the session.
- Motion is limited to short colour transitions, only under `prefers-reduced-motion: no-preference`.

### Optional: per-site app-switcher labels and branding

Both features read one optional key from a site's own `site_config.json`, `company_ui_brand`.
Without that key nothing changes, and this repository ships no branding values or logo files.

```json
"company_ui_brand": {
	"product_name": "<Product name>",
	"product_app": "hrms",
	"product_mark": "/files/<product-icon>.png",
	"app_titles": {"erpnext": "<Label>", "frappe": "<Label>"},
	"app_tile_roles": {"erpnext": ["System Manager"]}
}
```

1. **`boot.py`** (`extend_bootinfo` hook) relabels the Desk app switcher, rail and sidebar header
   on every boot: the `product_app` gets `product_name` and `product_mark`; apps in `app_titles`
   get that label and Frappe's letter icon. `app_tile_roles` hides an app's tile from users with
   none of the listed roles. This is display-only; access to those pages is unchanged.
2. **`branding.py`** writes branding settings once, only when run explicitly for one site:

   ```bash
   bench --site <your-site> execute company_ui_theme.branding.apply
   ```

   It is idempotent and prints every value it changes with its previous value. Record the
   current values before running it, because it does not undo itself.

   | Key | Writes |
   | --- | --- |
   | `product_name` | Website Settings and System Settings → App Name |
   | `logo` | Website Settings → App Logo |
   | `splash` | Website Settings → Splash Image |
   | `favicon` | Website Settings → FavIcon |
   | `footer_text` | Website Settings → Footer "Powered" text |
   | `disable_standard_email_footer` | System Settings |
   | `hide_help_items` | Navbar Settings → Help dropdown items hidden |
   | `translations` | English Translation records (`{"source": "translated"}`) |

   Upload any logo or icon through Desk (File Manager) and reference its `/files/...` URL;
   do not add company assets to this repository.

Do not add an `app_logo_url` hook to this app: Frappe picks `logos[1]` only when there are exactly
two hook entries, so a third entry silently falls back to Frappe's own logo.

### Uninstalling

```bash
bench --site <your-site> uninstall-app company_ui_theme
bench remove-app company_ui_theme --no-backup   # removes the link, the package and the apps.txt entry
bench --site <your-site> clear-cache
```

Use `--no-backup`: it deletes only the `apps/company_ui_theme` link and leaves the source in
`apps/hrms/custom_apps/` untouched. Without it, bench tries to move the link into `archived/apps/`,
which fails on benches without that folder and would leave a dangling relative link anyway.

Settings written by `branding.py` stay in the database until changed back in Website Settings,
System Settings, Navbar Settings and Translation.

### Limitations and manual checks

- The HRMS mobile PWA (`/hrms`, Vue + frappe-ui) and public website pages do not load Desk
  includes, so this theme does not apply there.
- Frappe Charts set their colours per chart in JavaScript; the theme does not change chart colours.
- Visual QA of HRMS screens in both themes needs a person in a browser: workspaces and charts,
  list views with filters, Employee / Leave Application / Salary Slip forms, child tables,
  dialogs, the notifications panel, report datatables, and mobile widths.

### Continuing development

- Build HR features in HRMS customisations (Custom Fields, Client Scripts, Property Setters) or a
  separate custom app, not here. This app should only contain UI styling.
- Use Frappe's standard components (`frappe.ui.Dialog`, form controls, list views); they pick up
  the theme automatically.
- To check the current theme in JS, use `frappe.ui.get_current_theme()` (`"light"` / `"dark"`).

### License

MIT
