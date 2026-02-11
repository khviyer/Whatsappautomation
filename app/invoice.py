from datetime import datetime
from pathlib import Path

from app.models import InvoiceLine


COMPANY_NAME = "XYZ Pvt Ltd"
COMPANY_ADDRESS = "Bengaluru, Karnataka"


def _escape_pdf_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _build_simple_pdf(lines: list[str]) -> bytes:
    content_lines = ["BT", "/F1 12 Tf", "50 790 Td"]
    for idx, line in enumerate(lines):
        safe_line = _escape_pdf_text(line)
        if idx == 0:
            content_lines.append(f"({safe_line}) Tj")
        else:
            content_lines.append("0 -16 Td")
            content_lines.append(f"({safe_line}) Tj")
    content_lines.append("ET")
    content_stream = "\n".join(content_lines).encode("latin-1", errors="replace")

    objects: list[bytes] = []
    objects.append(b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n")
    objects.append(b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n")
    objects.append(
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n"
    )
    objects.append(b"4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n")
    objects.append(
        f"5 0 obj << /Length {len(content_stream)} >> stream\n".encode("latin-1")
        + content_stream
        + b"\nendstream endobj\n"
    )

    pdf = bytearray(b"%PDF-1.4\n")
    xref_positions = [0]
    for obj in objects:
        xref_positions.append(len(pdf))
        pdf.extend(obj)

    xref_start = len(pdf)
    pdf.extend(f"xref\n0 {len(xref_positions)}\n".encode("latin-1"))
    pdf.extend(b"0000000000 65535 f \n")
    for pos in xref_positions[1:]:
        pdf.extend(f"{pos:010d} 00000 n \n".encode("latin-1"))

    trailer = (
        f"trailer << /Size {len(xref_positions)} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF\n"
    ).encode("latin-1")
    pdf.extend(trailer)
    return bytes(pdf)


def create_invoice_pdf(
    invoice_number: str,
    branch_id: str,
    customer_name: str,
    lines: list[InvoiceLine],
    subtotal: float,
    gst_total: float,
    discount: float,
    total: float,
    payment_link: str,
    output_dir: str = "invoices",
) -> str:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    date_label = datetime.now().strftime("%Y-%m-%d %H:%M")

    pdf_lines = [
        COMPANY_NAME,
        COMPANY_ADDRESS,
        f"Tax Invoice: {invoice_number}",
        f"Date: {date_label}",
        f"Buyer: {customer_name}",
        f"Branch: {branch_id}",
        "-" * 50,
        "Item | Qty | Unit Price | GST% | Line Total",
    ]
    for line in lines:
        pdf_lines.append(
            f"{line.item} | {line.qty} | INR {line.unit_price:.2f} | {line.gst_rate * 100:.1f}% | INR {line.line_total:.2f}"
        )

    pdf_lines.extend(
        [
            "-" * 50,
            f"Subtotal: INR {subtotal:.2f}",
            f"GST Total: INR {gst_total:.2f}",
            f"Discount: INR {discount:.2f}",
            f"Total Due: INR {total:.2f}",
            f"Payment Link: {payment_link}",
            "If any correction is needed, reply on WhatsApp with invoice number.",
        ]
    )

    pdf_bytes = _build_simple_pdf(pdf_lines)
    pdf_path = Path(output_dir) / f"{invoice_number}.pdf"
    pdf_path.write_bytes(pdf_bytes)
    return str(pdf_path)
