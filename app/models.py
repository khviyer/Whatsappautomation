from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class ParsedItem:
    item: str
    qty: int
    variant: str | None = None
    note: str | None = None


@dataclass
class IncomingWhatsAppMessage:
    customer_name: str
    customer_phone: str
    branch_id: str = "main"
    message_type: str = "text"
    message: str | None = None
    audio_transcript: str | None = None
    promo_code: str | None = None
    special_note: str | None = None


@dataclass
class InvoiceLine:
    item: str
    qty: int
    unit_price: float
    gst_rate: float
    taxable_total: float
    gst_amount: float
    line_total: float


@dataclass
class InvoiceResult:
    invoice_number: str
    branch_id: str
    gst_rate: str
    subtotal: float
    gst_total: float
    discount: float
    total: float
    pdf_generated: bool
    pdf_path: str
    payment_link: str
    created_at: datetime = field(default_factory=datetime.now)

    def as_dict(self) -> dict[str, str | float | bool]:
        return {
            "invoice_number": self.invoice_number,
            "branch_id": self.branch_id,
            "gst_rate": self.gst_rate,
            "subtotal": self.subtotal,
            "gst_total": self.gst_total,
            "discount": self.discount,
            "total": self.total,
            "pdf_generated": self.pdf_generated,
            "pdf_path": self.pdf_path,
            "payment_link": self.payment_link,
            "created_at": self.created_at.isoformat(),
        }
