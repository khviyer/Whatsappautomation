import os
import unittest

from app.main import process_revision_request, process_whatsapp_order
from app.models import IncomingWhatsAppMessage
from app.parser import parse_order_text
from app.pricing import price_items


class BillingAutomationTests(unittest.TestCase):
    def test_parse_with_autocorrect_and_quantities(self) -> None:
        items = parse_order_text("Kindly dispatch 10 thermal rool, 2 label pack")
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].item, "thermal paper roll")
        self.assertEqual(items[0].qty, 10)
        self.assertEqual(items[1].item, "barcode label pack")

    def test_price_items_with_discount(self) -> None:
        items = parse_order_text("2 shipping box, 1 packing tape")
        lines, subtotal, gst_total, discount, total = price_items(items, promo_code="BULK5")

        self.assertEqual(len(lines), 2)
        self.assertGreater(subtotal, 0)
        self.assertGreater(gst_total, 0)
        self.assertGreater(discount, 0)
        self.assertEqual(total, round(subtotal + gst_total - discount, 2))

    def test_end_to_end_invoice_generation(self) -> None:
        payload = IncomingWhatsAppMessage(
            customer_name="Acme Retail",
            customer_phone="+919999999999",
            branch_id="blr-01",
            message_type="text",
            message="please dispatch 3 thermal paper roll, 1 packing tape",
            promo_code="BULK5",
        )
        result = process_whatsapp_order(payload)

        self.assertTrue(result.invoice_number.startswith("INV-"))
        self.assertTrue(result.pdf_generated)
        self.assertTrue(os.path.exists(result.pdf_path))

        with open(result.pdf_path, "rb") as handle:
            self.assertTrue(handle.read(8).startswith(b"%PDF"))

    def test_revision_loop_helper(self) -> None:
        response = process_revision_request("INV-2026-00099", "Please change qty for shipping box to 4")
        self.assertEqual(response["status"], "revision_requested")


if __name__ == "__main__":
    unittest.main()
