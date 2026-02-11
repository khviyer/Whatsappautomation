from collections import defaultdict

from app.catalog import PRODUCT_CATALOG, PROMO_CODES
from app.models import InvoiceLine, ParsedItem


def price_items(items: list[ParsedItem], promo_code: str | None = None) -> tuple[list[InvoiceLine], float, float, float, float]:
    lines: list[InvoiceLine] = []
    subtotal = 0.0
    gst_total = 0.0

    grouped: dict[str, int] = defaultdict(int)
    for item in items:
        grouped[item.item] += item.qty

    for name, qty in grouped.items():
        if name not in PRODUCT_CATALOG:
            continue
        product = PRODUCT_CATALOG[name]
        taxable_total = qty * product.unit_price
        gst_amount = taxable_total * product.gst_rate
        line_total = taxable_total + gst_amount

        lines.append(
            InvoiceLine(
                item=product.name,
                qty=qty,
                unit_price=product.unit_price,
                gst_rate=product.gst_rate,
                taxable_total=round(taxable_total, 2),
                gst_amount=round(gst_amount, 2),
                line_total=round(line_total, 2),
            )
        )
        subtotal += taxable_total
        gst_total += gst_amount

    discount_rate = PROMO_CODES.get((promo_code or "").upper(), 0.0)
    discount = (subtotal + gst_total) * discount_rate
    total = subtotal + gst_total - discount

    return lines, round(subtotal, 2), round(gst_total, 2), round(discount, 2), round(total, 2)
