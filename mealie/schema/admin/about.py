from mealie.schema._mealie import MealieModel


class AppStatistics(MealieModel):
    total_recipes: int
    total_users: int
    total_households: int
    total_groups: int
    uncategorized_recipes: int
    untagged_recipes: int


class AppInfo(MealieModel):
    production: bool
    version: str
    demo_status: bool
    allow_signup: bool
    allow_password_login: bool
    default_group_slug: str | None = None
    default_household_slug: str | None = None
    enable_oidc: bool
    oidc_redirect: bool
    oidc_provider_name: str
    enable_reverse_proxy_auth: bool
    token_time: int
    allowed_iframe_hosts: list[str] = []
    branding_name: str = "Mealie"
    branding_logo_url: str | None = None


class AppTheme(MealieModel):
    light_primary: str = "#0D9488"
    light_accent: str = "#6366F1"
    light_secondary: str = "#E11D48"
    light_success: str = "#16A34A"
    light_info: str = "#2563EB"
    light_warning: str = "#D97706"
    light_error: str = "#DC2626"

    dark_primary: str = "#2DD4BF"
    dark_accent: str = "#818CF8"
    dark_secondary: str = "#FB7185"
    dark_success: str = "#4ADE80"
    dark_info: str = "#60A5FA"
    dark_warning: str = "#FBBF24"
    dark_error: str = "#F87171"


class AppStartupInfo(MealieModel):
    is_first_login: bool
    """
    The applications best guess that a user hasn't logged in. Currently, it really
    on indicates that the 'changeme@example.com' user is still in the database. Once
    it is removed, this will always return False.
    """

    is_demo: bool


class AdminAboutInfo(AppInfo):
    versionLatest: str
    api_port: int
    api_docs: bool
    db_type: str
    db_url: str | None = None
    default_group: str
    default_household: str
    build_id: str
    recipe_scraper_version: str


class CheckAppConfig(MealieModel):
    email_ready: bool
    ldap_ready: bool
    ldap_disabled: bool
    oidc_ready: bool
    oidc_disabled: bool
    reverse_proxy_auth_ready: bool
    reverse_proxy_auth_disabled: bool
    base_url_set: bool
    is_up_to_date: bool
