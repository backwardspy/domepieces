from contextlib import contextmanager
from typing import Iterator

import plyvel


@contextmanager
def open_db(path: str) -> Iterator[plyvel.DB]:
    db = plyvel.DB(path, create_if_missing=True)
    try:
        yield db
    finally:
        db.close()
