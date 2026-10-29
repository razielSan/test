class TestSettings:
    POSTGRESQL_NAME_DATABASE: str = "postgresql"
    SQLITE_NAME_DATABASE: str = "sqlite"


test_settings = TestSettings()
names_test_databases = [
    test_settings.POSTGRESQL_NAME_DATABASE,
    test_settings.SQLITE_NAME_DATABASE,
]
