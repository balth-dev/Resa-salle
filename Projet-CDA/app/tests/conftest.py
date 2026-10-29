# Tests use an in-memory SQLite fixture in test_user_repository.py.
# Do not drop/create tables on the application engine here: a previous
# autouse fixture pointed at a missing "tests/ .env.test" file (note the
# space) and then called drop_all() against the real database.