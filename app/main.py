import json
from urllib.parse import quote_plus

from app.invoice import create_invoice_pdf
from app.models import IncomingWhatsAppMessage, InvoiceResult
from app.parser import parse_order_text
from app.pricing import price_items
from app.storage import STORE


def send_invoice_to_whatsapp(phone: str, pdf_path: str, invoice_number: str) -> dict[str, str]:
    """Placeholder integration function for Meta/Twilio WhatsApp APIs."""
    return {
        "status": "queued",
        "phone": phone,
        "document": pdf_path,
        "message": f"Invoice {invoice_number} has been generated and queued for WhatsApp delivery.",
    }


def process_whatsapp_order(payload: IncomingWhatsAppMessage) -> InvoiceResult:
    if payload.message_type not in {"text", "voice"}:
        raise ValueError("message_type must be 'text' or 'voice'")

    raw_message = payload.message if payload.message_type == "text" else payload.audio_transcript
    if not raw_message:
        raise ValueError("No message content found")

    parsed_items = parse_order_text(raw_message, payload.special_note)
    if not parsed_items:
        raise ValueError("No valid items found in order")

    invoice_lines, subtotal, gst_total, discount, total = price_items(parsed_items, payload.promo_code)
    if not invoice_lines:
        raise ValueError("None of the requested items are configured in catalog")

    invoice_number = STORE.next_invoice_number()
    payment_link = f"https://pay.razorpay.com/?invoice={quote_plus(invoice_number)}&amount={int(total * 100)}"
    pdf_path = create_invoice_pdf(
        invoice_number=invoice_number,
        branch_id=payload.branch_id,
        customer_name=payload.customer_name,
        lines=invoice_lines,
        subtotal=subtotal,
        gst_total=gst_total,
        discount=discount,
        total=total,
        payment_link=payment_link,
    )

    for item in parsed_items:
        STORE.deduct_inventory(item.item, item.qty)

    invoice = InvoiceResult(
        invoice_number=invoice_number,
        branch_id=payload.branch_id,
        gst_rate="mixed",
        subtotal=subtotal,
        gst_total=gst_total,
        discount=discount,
        total=total,
        pdf_generated=True,
        pdf_path=pdf_path,
        payment_link=payment_link,
    )
    STORE.save_invoice(invoice)
    send_invoice_to_whatsapp(payload.customer_phone, pdf_path, invoice_number)
    return invoice


def process_revision_request(invoice_number: str, customer_message: str) -> dict[str, str]:
    return {
        "invoice_number": invoice_number,
        "status": "revision_requested",
        "message": f"Revision noted for {invoice_number}: {customer_message}",
    }


def get_daily_summary(branch_id: str | None = None) -> dict[str, float | int]:
    return STORE.daily_summary(branch_id=branch_id)


def get_inventory() -> dict[str, int]:
    return STORE.inventory_snapshot()


def demo() -> None:
    sample = IncomingWhatsAppMessage(
        customer_name="Acme Retail",
        customer_phone="+919999999999",
        branch_id="blr-01",
        message_type="text",
        message="Hi, please dispatch 10 thermal paper roll, 5 barcode label pack, 3 shipping box",
        promo_code="BULK5",
    )
    result = process_whatsapp_order(sample)
    print(json.dumps(result.as_dict(), indent=2))


if __name__ == "__main__":
    demo()
