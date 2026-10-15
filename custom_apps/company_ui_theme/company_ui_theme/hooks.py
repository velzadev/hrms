app_name = "company_ui_theme"
app_title = "Company UI Theme"
app_publisher = "Community"
app_description = "Reusable light/dark Desk UI theme for Frappe HRMS v16"
app_license = "mit"

# Includes in <head>
# ------------------

# Desk only (desk.html). The website, the login page and the HRMS PWA at /hrms do not load these.
# Both are plain (non-bundle) files served from /assets/company_ui_theme/.
app_include_css = ["/assets/company_ui_theme/css/company_ui_theme.css"]
app_include_js = ["/assets/company_ui_theme/js/company_ui_theme.js"]

# Boot
# ----

# Optional per-site relabelling of the Desk app switcher. It does nothing unless the site's
# site_config.json has a `company_ui_brand` key (see boot.py and the README).
extend_bootinfo = "company_ui_theme.boot.extend_bootinfo"
