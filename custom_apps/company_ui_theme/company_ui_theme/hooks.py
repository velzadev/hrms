app_name = "company_ui_theme"
app_title = "Company UI Theme"
app_publisher = "Community"
app_description = "Reusable light/dark Desk UI theme for Frappe HRMS v16"
app_license = "mit"

import hashlib as _hashlib
from pathlib import Path as _Path

_PUBLIC = _Path(__file__).parent / "public"


def _asset(path):
	"""URL of a plain (non-bundle) asset with a content hash, so browsers fetch every new version.

	Frappe serves /assets with a 12-hour cache and includes plain files without a version, so
	without this a theme update would not reach browsers that loaded the old file.
	"""
	url = f"/assets/company_ui_theme/{path}"
	try:
		return f"{url}?v={_hashlib.sha1((_PUBLIC / path).read_bytes()).hexdigest()[:10]}"
	except OSError:
		return url


# Includes in <head>
# ------------------

# Desk only (desk.html). The website, the login page and the HRMS PWA at /hrms do not load these.
app_include_css = [_asset("css/company_ui_theme.css")]
app_include_js = [
	_asset("js/company_ui_theme.js"),
	_asset("js/company_ui_theme_menus.js"),
]

# Website pages. Every rule in this file is scoped to the login and update-password pages.
web_include_css = [_asset("css/company_ui_theme_web.css")]

# Boot
# ----

# Quicxly labels for the HRMS app tile, switcher and product-name strings in Desk. A site can
# override them with a `company_ui_brand` key in its site_config.json (see boot.py and the README).
extend_bootinfo = "company_ui_theme.boot.extend_bootinfo"

# Quicxly as the product name in the browser title and on the login page, unless the site has set
# its own App Name (see website.py).
update_website_context = "company_ui_theme.website.update_website_context"
