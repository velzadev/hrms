## Company UI Theme

The Quicxly visual theme for the Frappe HRMS v16 Desk (Frappe v16, ERPNext v16, HRMS v16).

| Branch | Theme in this folder |
| --- | --- |
| `main` | **Quicxly** (this README) |
| `version-16` | Brand-neutral (Frappe's own colours) |

It is a pure UI layer: no DocTypes, no patches, no database changes, and no Frappe, ERPNext or
HRMS files are modified. It adds:

- **Quicxly dashboard styling** for Desk: the coral/orange brand on primary buttons, focus rings,
  checkboxes, tabs, selected sidebar rows and list rows, the active rail tile and a thin gradient
  stripe under each page header; plus rounded corners, 1px borders, soft shadows in light mode
  and flat cards in dark mode. Surfaces, text and borders stay Frappe's own theme variables.
- **Login page styling**: brand primary button, focus ring and a gradient accent on the login and
  update-password pages only.
- **A light/dark toggle** in every page header, kept in sync with Frappe's own theme switcher.
- **Optional, per-site relabelling** of the Desk app switcher (off unless configured), and an
  optional script that writes per-site branding settings. Neither ships any branding.

The app is kept in the `velzadev/hrms` repository under `custom_apps/company_ui_theme/`, separate
from the `hrms` Python package. It is a normal Frappe app with its own `pyproject.toml` and
`hooks.py`; it is just not at the root of its own Git repository, so it is linked into the bench
instead of being fetched with `bench get-app`.

### Requirements

- A Frappe v16 bench with Frappe, ERPNext and HRMS v16 (Python 3.14, as for Frappe v16)
- HRMS fetched from `https://github.com/velzadev/hrms`, which contains this folder: branch
  `main` for the Quicxly theme, `version-16` for the neutral one

### Installation

Run from the bench directory (the one containing `apps/`, `sites/` and `env/`):

```bash
# 1. Get HRMS from this repository, if the bench does not have it yet
#    (use --branch version-16 instead for the neutral theme)
bench get-app https://github.com/velzadev/hrms --branch main

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
| `company_ui_theme/public/css/company_ui_theme.css` | Quicxly brand tokens, shape and elevation tokens, Desk component rules, toggle styles |
| `company_ui_theme/public/css/company_ui_theme_web.css` | Login and update-password page styling (scoped to those pages) |
| `company_ui_theme/public/js/company_ui_theme.js` | Theme controller: saved preference, header toggle, sync with Frappe's switcher |
| `company_ui_theme/public/js/company_ui_theme_menus.js` | Hides upstream-product rows (Frappe School, About, …) from the Desk Help menu, using rules sent by `boot.py` |
| `company_ui_theme/public/images/` | Quicxly logo assets (temporary; see its README) |
| `company_ui_theme/hooks.py` | Includes the Desk CSS/JS (`app_include_css` / `app_include_js`) and the login CSS (`web_include_css`), registers `boot.py` and `website.py` |
| `company_ui_theme/boot.py` | Quicxly label for the HRMS app tile, switcher and rail; optional per-site overrides (see below) |
| `company_ui_theme/website.py` | Quicxly as the default app name in the browser title (`update_website_context` hook) |
| `company_ui_theme/translations/en.csv` | English display strings that name the product ("Frappe HR" → "Quicxly") |
| `company_ui_theme/branding.py` | Optional per-site branding script (see below) |

While `bench start` is running, a hard refresh is enough after editing them. Run
`bench build --app company_ui_theme` after adding new files or on a fresh bench. Desk includes
these files without a version query, so after deploying a change run `bench clear-cache` and ask
users to hard-refresh.

To restyle, change only the tokens in section 1 of `company_ui_theme.css` (`--qx-*` brand colours,
`--ui-theme-*` radii and shadows), and the matching block at the top of
`company_ui_theme_web.css`. For neutral colours, use Frappe's variables (`var(--text-color)`,
`var(--text-muted)`, `var(--border-color)`, `var(--card-bg)`, `var(--fg-color)`) instead of
hard-coded values, and test both themes.

### Quicxly brand tokens

The reference colours are estimates taken from the Quicxly brand images and are meant to be
adjusted once official values are available. Filled controls that carry text use deeper or
lighter shades of the same hue so that text meets WCAG AA (4.5:1); the true gradient is used only
for decorative accents, with dark glyphs on it.

| Token | Light | Dark | Used for |
| --- | --- | --- | --- |
| `--qx-coral` / `--qx-orange` | `#FF626F` / `#FF8B3D` | same | Brand reference; sidebar and notification edges |
| `--qx-gradient` | coral → orange, 135° | same | Header stripe, active rail tile, login accent |
| `--qx-on-gradient` | `#171717` | same | Glyphs on the gradient (6.2–7.7:1) |
| `--qx-primary` | `#D03246` | `#FF7A85` | Primary buttons, checkboxes, active tabs |
| `--qx-on-primary` | `#FFFFFF` (5.0:1) | `#171717` (7.2:1) | Text on primary fills |
| `--qx-primary-hover` / `-active` | `#B72B40` / `#A32539` | `#FF8C95` / `#FF626F` | Button states |
| `--qx-accent-text` | `#C42F45` (5.5:1 on white) | `#FF8C95` | Coloured link and icon text |
| `--qx-tint` / `--qx-tint-strong` | coral at 10% / 16% | 14% / 22% | Selected sidebar rows, list rows, rail hover |
| `--qx-focus-ring` | coral 2px | coral 2px | Focus on inputs, buttons, checkboxes, tabs |

**Logo:** the logo files in `public/images/` are **temporary** assets cut from the only supplied
logo, a WhatsApp-compressed JPEG (see `public/images/README.md`). Replace them with the official
transparent originals when available. Only the mark is used on dark surfaces, because no
light/white wordmark has been supplied.

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

### Quicxly branding (white-label)

Out of the box, with no configuration and no database changes, Desk is presented as **Quicxly™**
(the ™ appears in the logo artwork, not in UI labels):

| Where | Before | After | How |
| --- | --- | --- | --- |
| Apps screen: HRMS tile | Frappe HR + Frappe HR logo | Quicxly + Quicxly mark | `boot.py` relabels `bootinfo.app_data` |
| Apps screen: ERPNext / Framework tiles | ERPNext / Framework + their logos | Business / Administration + neutral letter icons | `boot.py` (`app_titles`) |
| Apps screen: top-left logo | Frappe logo | Quicxly mark | CSS (only Frappe's built-in fallback image is swapped; see note) |
| Sidebar header logo for the HRMS app | Frappe HR logo | Quicxly mark | `boot.py` |
| Login and update-password pages | Frappe logo | Quicxly logo (mark + wordmark) | `website.py` (`update_website_context`) |
| Favicon (login and Desk) | ERPNext favicon | Quicxly mark | `website.py` |
| Desk loading splash | ERPNext logo | Quicxly mark (light and dark) | `website.py` |
| Browser title of the Desk shell | Frappe | Quicxly | `website.py` |
| HR / ERPNext onboarding, ERPNext Settings | Frappe HR, ERPNext | Quicxly, Business | `translations/en.csv` |
| User menu (apps screen) | About, Frappe Support | removed | CSS (Frappe hard-codes them) |
| Sidebar Help menu | Documentation, User Forum, Frappe School, Report an Issue, About, Frappe Support (all upstream sites) | removed; System Health and any site-added rows stay | `company_ui_theme_menus.js`, rules from `boot.py` |
| Sidebar advertisement | "Switch to Frappe CRM" | hidden | CSS |

Routes, permissions, installed app names and Python packages are unchanged; every app stays
reachable. Hidden menu rows are hidden in the browser only (Navbar Settings is not edited).

Precedence: a logo, favicon, splash or App Name set in the site's Website / Navbar / System
Settings, and the site's Translation records, always win over these defaults; any key in
`company_ui_brand` (below) overrides the built-in default.

The apps-screen top-left logo is rendered server-side from Navbar Settings → App Logo, which no
theme hook can reach, so the CSS swaps Frappe's default image there. Setting Navbar Settings →
App Logo on a site is the fully supported alternative.

### Optional: per-site app-switcher labels and branding

Both features read one optional key from a site's own `site_config.json`, `company_ui_brand`.
For the app labels, any key given there overrides the built-in Quicxly default above; this
repository ships no logo files.

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
   on every boot: the `product_app` (default `hrms`) gets `product_name` (default `Quicxly`) and
   `product_mark`; apps in `app_titles`
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

- The HRMS mobile PWA (`/hrms`, Vue + frappe-ui) does not load Desk includes, so this theme does
  not apply there. Of the public website pages, only the login and update-password pages are
  styled.
- Frappe Charts set their colours per chart in JavaScript; the theme does not change chart colours.
- The Quicxly colours are estimates from the brand images, and the logo assets are temporary
  (see "Quicxly brand tokens" and `public/images/README.md`).
- Still showing upstream names, outside this theme's reach: the About dialog content (no longer
  reachable from the menus), Frappe's error and maintenance pages, system/setup screens that print
  "Frappe" or "ERPNext" in field help text, email footers, the "Frappe" watermark inside HRMS's
  onboarding video thumbnail, technical URLs (`/assets/frappe/...`), app/package names, and logs.
- The English translation file only relabels English UI text; other languages show their own
  translations.
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
