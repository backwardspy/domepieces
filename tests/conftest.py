import shutil
import tempfile

import pytest


@pytest.fixture
def db_path(request: pytest.FixtureRequest) -> str:
    name = tempfile.mkdtemp()
    request.addfinalizer(lambda: shutil.rmtree(name))
    return name
