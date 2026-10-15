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

# Website pages. Every rule in this file is scoped to the login and update-password pages.
web_include_css = ["/assets/company_ui_theme/css/company_ui_theme_web.css"]

# Boot
# ----

# Qulix labels for the HRMS app tile, switcher and product-name strings in Desk. A site can
# override them with a `company_ui_brand` key in its site_config.json (see boot.py and the README).
extend_bootinfo = "company_ui_theme.boot.extend_bootinfo"

# Qulix as the product name in the browser title and on the login page, unless the site has set
# its own App Name (see website.py).
update_website_context = "company_ui_theme.website.update_website_context"
