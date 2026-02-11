from dataclasses import dataclass


@dataclass(frozen=True)
class Product:
    name: str
    unit_price: float
    gst_rate: float
    aliases: tuple[str, ...] = ()


# Example B2B catalog for a generic company (e.g. XYZ Pvt Ltd)
PRODUCT_CATALOG: dict[str, Product] = {
    "thermal paper roll": Product(
        name="thermal paper roll",
        unit_price=65.0,
        gst_rate=0.12,
        aliases=("paper roll", "thermal roll"),
    ),
    "barcode label pack": Product(
        name="barcode label pack",
        unit_price=220.0,
        gst_rate=0.12,
        aliases=("label pack", "barcode labels"),
    ),
    "shipping box": Product(
        name="shipping box",
        unit_price=35.0,
        gst_rate=0.18,
        aliases=("carton box", "box"),
    ),
    "packing tape": Product(
        name="packing tape",
        unit_price=30.0,
        gst_rate=0.18,
        aliases=("tape",),
    ),
    "invoice printing service": Product(
        name="invoice printing service",
        unit_price=12.0,
        gst_rate=0.18,
        aliases=("printing service",),
    ),
}

PROMO_CODES: dict[str, float] = {
    "BULK5": 0.05,
    "BULK10": 0.10,
}
