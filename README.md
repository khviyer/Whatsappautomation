# Whatsappautomation

Simple B2B WhatsApp invoice generator for businesses like **XYZ Pvt Ltd**.
Customers place an order on WhatsApp, the system parses the message, generates an invoice PDF, and prepares the invoice to be sent back to the buyer.

## What this project does
- Parses natural-language order messages from WhatsApp text or voice transcript.
- Auto-corrects minor spelling mistakes for known products.
- Calculates invoice totals with GST and optional promo discounts.
- Generates a tax invoice PDF.
- Creates a payment link and simulates WhatsApp delivery.
- Supports invoice revision loop (customer replies with modifications).

## Example inbound WhatsApp message
`Hi, please dispatch 10 thermal paper roll, 5 barcode label pack, 3 shipping box`

## Example output JSON
```json
{
  "invoice_number": "INV-2026-00045",
  "branch_id": "blr-01",
  "gst_rate": "mixed",
  "subtotal": 1830.0,
  "gst_total": 251.4,
  "discount": 104.07,
  "total": 1977.33,
  "pdf_generated": true,
  "pdf_path": "invoices/INV-2026-00045.pdf",
  "payment_link": "https://pay.razorpay.com/?invoice=INV-2026-00045&amount=197733"
}
```

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate
python -m unittest discover -s tests -v
python -m app.main
```

## Important modules
- `app/parser.py`: order parsing + autocorrect.
- `app/pricing.py`: GST/discount computation.
- `app/invoice.py`: PDF invoice creation.
- `app/main.py`: orchestration + WhatsApp send stub + revision loop helper.
- `app/storage.py`: invoice numbering, inventory, daily summaries.

## Production integration
- Replace `send_invoice_to_whatsapp()` with actual Meta WhatsApp Cloud API or Twilio client call.
- Persist invoices/orders in PostgreSQL.
- Expose as webhook endpoint using FastAPI/Flask if needed.
