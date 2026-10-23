# Testing

The project uses `pytest` and `pytest-asyncio`.


## 1 Test Run

To run the tests, you need to specify the name of the test database

Run api tests

```bash
run_test_api.py sqlite
```

Run integration tests

```bash
run_test_integration.py sqlite
```

Run page tests

```bash
run_test_page.py sqlite
```

### Available databases

[supported databases](./src/infrastructure/db/settings.py)

***

## 2. Test structure

### TODO: заполнить

The tests use the UnitOfWorkProtocol, so the tests themselves do not depend on a specific database implementation.

***

## 3. Cleaning the test database

After each test, the database is cleared via a fixture:

```python
get_uwo
```

**At the same time, the role table is preserved, since roles are the initial data of the test database.**

The databases that are created in the project directory after the test will be deleted.

***

# 4. Adding a new test base

1. Add a new path to [follow the link](./src/test_data/paths.py)
2. Add a new database name to [follow the link](./src\infrastructure\db\settings.py)
3. Create an appropriate Backend in [follow the link](./src/test_data/db/)
4. Add **Backend** and **path** to **StorageBackend**. Associate **DatabaseName** with **StorageBackend**  to **DATABASE_BACKENDS** in . [follow the link](./src/test_data/utils.py)

