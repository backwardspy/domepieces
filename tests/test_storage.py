from typing import Optional

import plyvel

from domepieces.storage import open_db


def test_open_db(db_path: str) -> None:
    """
    Test that the open_db function opens a database at the given path.
    """
    with open_db(db_path) as db:
        assert db is not None
        assert db.name == db_path
        assert db.closed is False

    assert db.closed is True


def test_db_is_closed_on_exception(db_path: str) -> None:
    """
    Test that the open_db function closes the database if an exception is raised.
    """
    test_db: Optional[plyvel.DB] = None
    try:
        with open_db(db_path) as db:
            test_db = db
            raise Exception("Test exception")
    except Exception:
        pass

    assert test_db is not None
    assert test_db.closed is True
