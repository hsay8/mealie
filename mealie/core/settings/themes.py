from pydantic_settings import BaseSettings, SettingsConfigDict


class Theme(BaseSettings):
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
    model_config = SettingsConfigDict(env_prefix="theme_", extra="allow")
