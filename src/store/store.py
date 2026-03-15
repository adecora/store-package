from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import TypedDict

print(files("store").joinpath("data/store.txt").read_text())


class Item(TypedDict):
    cmin: int
    cmax: int
    place: str
    description: str
    price: int


class Store(TypedDict):
    products: dict[str, Item]
    stock: dict[str, int]
    anomalies: set[str]
    restock: set[str]


# Correción del test `price: 1.2 -> price: 12` aunque no da un error, el linter se queja porque Item define `price` como un entero
def make_item(cmin: int, cmax: int, place: str, description: str, price: int) -> Item:
    """
    This function creates a dictionary fom the given parameteres.

    >>> print(make_item(25, 100, "001_AA", "Tornillos con cabeza grande", 12))
    {'cmin': 25, 'cmax': 100, 'place': '001_AA', 'description': 'Tornillos con cabeza grande', 'price': 12}
    """
    if cmin < 0 or cmax < 1 or price <= 0:
        raise ValueError("cmin, cmax and price must be positive")

    return {
        "cmin": cmin,
        "cmax": cmax,
        "place": place,
        "description": description,
        "price": price,
    }


def get_data(line: str) -> tuple[str, Item, int, bool, bool]:
    """
    This function analyzes a line from the file.

    >>> get_data('F01//25//70//100//001_AA//Tornillos con cabeza grande//3.21//False//False')
    ('F01', {'cmin': 25, 'cmax': 100, 'place': '001_AA', 'description': 'Tornillos con cabeza grande', 'price': 321}, 70, False, False)
    """
    (
        code,
        cmin_s,
        nitems_s,
        cmax_s,
        place,
        description,
        price_s,
        anomaly_s,
        restock_s,
    ) = line.split("//")
    cmin = int(cmin_s)
    cmax = int(cmax_s)
    price = round(float(price_s) * 100)
    nitems = int(nitems_s)
    anomaly = anomaly_s == "True"
    restock = restock_s == "True"
    item = make_item(cmin, cmax, place, description, price)
    return code, item, nitems, anomaly, restock


def read_data(filename: str | Path | Traversable | None = None) -> Store:
    """
    This function reads a file with the required format. It returns store dictionary
    >>> sorted(list(read_data('data/store.txt').keys()))
    ['anomalies', 'products', 'restock', 'stock']
    """
    if filename is None:
        # Ver: https://docs.python.org/3/library/importlib.resources.html
        # Ver: https://docs.python.org/3/library/importlib.resources.abc.html#importlib.resources.abc.Traversable
        # `importlib.resources.files` devuelve un objeto `importlib.resources.abc.Traversable` que se trata de un subset de `pathlib.Path`
        # Se incluye en el tipado de `filename`
        filename = files("store").joinpath("data/store.txt")
    elif isinstance(filename, str):
        filename = Path(filename)
    # Ver: https://docs.python.org/3/library/pathlib.html#pathlib.Path.open
    # Se modifica para usar el método `open` del objeto `filename` que es un `importlib.resources.abc.Traversable` o un `pathlib.Path`
    with filename.open() as fin:
        products, stock = dict(), dict()
        anomalies = set()
        restocks = set()
        for line in fin:
            code, item, nitems, anomaly, restock = get_data(line[:-1])
            products[code] = item
            stock[code] = nitems
            if anomaly:
                anomalies.add(code)
            if restock:
                restocks.add(code)

    return {
        "products": products,
        "stock": stock,
        "anomalies": anomalies,
        "restock": restocks,
    }


def sell(store: Store, code: str, nitems: int) -> None:
    """
    This functions sells an item.

    :param store:
    :param code:
    :param nitems:
    :return:
    """
    if store["stock"][code] >= nitems:
        store["stock"][code] -= nitems
        if store["products"][code]["cmin"] > store["stock"][code]:
            store["restock"].add(code)
    else:
        store["anomalies"].add(code)


def value(store: Store) -> int:
    """
    This function returns the value of the stock.
    """
    value = 0
    for code in store["products"]:
        value += store["products"][code]["price"] * store["stock"][code]
    return value


def save(filename: str, storage: Store) -> None:
    """
    This function saves the store in a file.
    """
    with open(filename, "w") as fout:
        for code in storage["products"]:
            cmin = storage["products"][code]["cmin"]
            cmax = storage["products"][code]["cmax"]
            place = storage["products"][code]["place"]
            description = storage["products"][code]["description"]
            price = storage["products"][code]["price"] / 100
            anomaly = code in storage["anomalies"]
            restock = code in storage["restock"]
            nitems = storage["stock"][code]
            line = f"{code}//{cmin}//{nitems}//{cmax}//{place}//{description}//{price:.2f}//{anomaly}//{restock}\n"
            fout.write(line)
