class TestSettings:
    POSTGRESQL_NAME_DATABASE = "postgresql"
    SQLITE_NAME_DATABASE = "sqlite"


test_settings = TestSettings()
names_test_databases = [
    test_settings.POSTGRESQL_NAME_DATABASE,
    test_settings.SQLITE_NAME_DATABASE,
]
