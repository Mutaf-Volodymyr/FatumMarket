JAZZMIN_SETTINGS = {
    "site_title": "Fatum Market",
    "site_header": "Fatum Market Admin",
    "site_brand": "Fatum",
    "welcome_sign": "Добро пожаловать!",
    "copyright": "Larez SRL.",
    "topmenu_links": [
        {"name": "Главная", "url": "/admin", "permissions": ["auth.view_user"]},
        {"name": "Товары", "url": "/admin/products/product/", "permissions": ["auth.view_user"]},
    ],
    "show_sidebar": True,
    "hide_app_list": False,
    "navigation_expanded": True,
    "changeform_format": "horizontal_tabs",
    # "changeform_format_overrides": {
    # }
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": True,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-dark",
    # "accent": "accent-dark",
    # "accent": "accent-secondary",
    "navbar": "navbar-dark",
    "footer": "footer-dark",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
    },
}
