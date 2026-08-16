from src.config.settings import Settings


def test_cors_origins_parses_comma_separated_values():
    settings = Settings(CORS_ORIGINS="https://app.example.com, https://admin.example.com")

    assert settings.cors_origins == [
        "https://app.example.com",
        "https://admin.example.com",
    ]


def test_cors_origins_keeps_local_wildcard():
    settings = Settings(CORS_ORIGINS="*")

    assert settings.cors_origins == ["*"]
