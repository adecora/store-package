import doctest
from pathlib import Path

import pytest

from store import get_data, make_item, read_data, save, sell, value

# Ver: https://github.com/omarkohl/pytest-datafiles/blob/main/examples/example_3.py
FIXTURE_DIR = Path(__file__).parent.resolve() / "test_files"

FILES = pytest.mark.datafiles(
    FIXTURE_DIR / "store1.txt",
    FIXTURE_DIR / "store2.txt",
)


@pytest.fixture
def files(datafiles):
    d = dict()
    for fname in datafiles.iterdir():
        d[fname.name] = fname.as_posix()
    return d


@pytest.fixture
def store1(files):
    return read_data(files["store1.txt"])


@pytest.fixture
def store2(files):
    return read_data(files["store2.txt"])


def test_make_item1():
    doctest.run_docstring_examples(make_item, globals())


@pytest.mark.parametrize(
    "cmin, price, code, name, expected",
    [
        (-5, 100, "001_AA", "Tornillos con cabeza grande", 12),
        (25, 0, "001_AA", "Tornillos con cabeza grande", 12),
        (25, 100, "001_AA", "Tornillos con cabeza grande", -12),
    ],
)
def test_make_item2(cmin, price, code, name, expected):
    with pytest.raises(ValueError):
        make_item(cmin, price, code, name, expected)


def test_get_data():
    doctest.run_docstring_examples(get_data, globals())


@FILES
def test_read_data(store1, store2):
    st = read_data()
    assert st["products"]["F01"]["cmin"] == 25

    assert store1["products"]["F10"]["cmin"] == 25

    assert store2["products"]["F10"]["cmin"] == 25
    assert store2["products"]["F01"]["cmin"] == 25


@FILES
def test_sell1(store1):
    assert store1["stock"]["F10"] == 50
    assert "F10" not in store1["anomalies"]

    sell(store1, "F10", 30)
    assert store1["stock"]["F10"] == 20
    assert "F10" in store1["restock"]

    sell(store1, "F10", 30)
    assert store1["stock"]["F10"] == 20
    assert "F10" in store1["anomalies"]


@FILES
def test_value(store1, store2):
    assert value(store1) == 215850

    assert value(store2) == 246980


@FILES
# Ver: https://docs.pytest.org/en/stable/how-to/tmp_path.html
def test_save1(tmp_path, store1):
    sell(store1, "F10", 20)
    sell(store1, "F10", 60)
    save(tmp_path / "res.txt", store1)
    stres = read_data(tmp_path / "res.txt")
    assert stres["stock"]["F10"] == 30
    assert "F10" in stres["anomalies"]
    assert "F10" in stres["stock"]
