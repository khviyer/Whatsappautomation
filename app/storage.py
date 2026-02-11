from collections import defaultdict
from datetime import datetime

from app.models import InvoiceResult


class InMemoryStore:
    def __init__(self) -> None:
        self._invoice_counter = 0
        self._invoices: list[InvoiceResult] = []
        self._inventory: dict[str, int] = defaultdict(lambda: 200)

    def next_invoice_number(self) -> str:
        self._invoice_counter += 1
        year = datetime.now().year
        return f"INV-{year}-{self._invoice_counter:05d}"

    def save_invoice(self, invoice: InvoiceResult) -> None:
        self._invoices.append(invoice)

    def deduct_inventory(self, item: str, qty: int) -> None:
        self._inventory[item] = max(0, self._inventory[item] - qty)

    def inventory_snapshot(self) -> dict[str, int]:
        return dict(self._inventory)

    def daily_summary(self, branch_id: str | None = None) -> dict[str, float | int]:
        today = datetime.now().date()
        filtered = [
            inv
            for inv in self._invoices
            if inv.created_at.date() == today and (branch_id is None or inv.branch_id == branch_id)
        ]
        revenue = sum(inv.total for inv in filtered)
        return {
            "order_count": len(filtered),
            "gross_revenue": round(revenue, 2),
        }


STORE = InMemoryStore()
