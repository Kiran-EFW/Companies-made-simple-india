"""Invoice and payment receipt generation for Indian companies."""
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class InvoiceService:
    """Generate GST-compliant invoices and payment receipts."""

    COMPANY_DETAILS = {
        "name": "Companies Made Simple India Private Limited",
        "address": "Bangalore, Karnataka, India",
        "gstin": "29XXXXX1234X1Z5",  # Placeholder
        "pan": "XXXXX1234X",  # Placeholder
        "sac_code": "998312",  # Legal advisory services
        "hsn_code": "9983",
    }

    def generate_invoice_html(
        self,
        invoice_number: str,
        customer_name: str,
        customer_email: str,
        customer_address: str,
        customer_gstin: Optional[str],
        items: List[Dict[str, Any]],  # [{description, amount, gst_rate}]
        payment_id: Optional[str] = None,
        invoice_date: Optional[datetime] = None,
    ) -> str:
        """Generate a GST-compliant invoice HTML."""
        date = invoice_date or datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)
        date_str = date.strftime("%d %B %Y")

        # Calculate totals
        subtotal = sum(item.get("amount", 0) for item in items)

        # Determine CGST+SGST or IGST based on customer state
        is_same_state = customer_gstin and customer_gstin[:2] == "29"  # Karnataka

        items_html = ""
        total_gst = 0
        for i, item in enumerate(items, 1):
            amount = item.get("amount", 0)
            gst_rate = item.get("gst_rate", 18)
            gst_amount = amount * gst_rate / 100
            total_gst += gst_amount

            items_html += (
                "<tr>"
                '<td style="padding:8px;border:1px solid #ddd;">{idx}</td>'
                '<td style="padding:8px;border:1px solid #ddd;">{desc}</td>'
                '<td style="padding:8px;border:1px solid #ddd;text-align:center;">{sac}</td>'
                '<td style="padding:8px;border:1px solid #ddd;text-align:right;">'
                "\u20b9{amount:,.2f}</td>"
                '<td style="padding:8px;border:1px solid #ddd;text-align:center;">'
                "{gst_rate}%</td>"
                '<td style="padding:8px;border:1px solid #ddd;text-align:right;">'
                "\u20b9{gst_amt:,.2f}</td>"
                '<td style="padding:8px;border:1px solid #ddd;text-align:right;">'
                "\u20b9{total:,.2f}</td>"
                "</tr>"
            ).format(
                idx=i,
                desc=item.get("description", ""),
                sac=self.COMPANY_DETAILS["sac_code"],
                amount=amount,
                gst_rate=gst_rate,
                gst_amt=gst_amount,
                total=amount + gst_amount,
            )

        grand_total = subtotal + total_gst

        # Amount in words helper
        amount_words = self._amount_in_words(int(grand_total))

        gst_breakdown = ""
        if is_same_state:
            half_gst = total_gst / 2
            gst_breakdown = (
                "<tr>"
                '<td colspan="6" style="padding:8px;border:1px solid #ddd;text-align:right;">CGST (9%):</td>'
                '<td style="padding:8px;border:1px solid #ddd;text-align:right;">'
                "\u20b9{half:,.2f}</td>"
                "</tr>"
                "<tr>"
                '<td colspan="6" style="padding:8px;border:1px solid #ddd;text-align:right;">SGST (9%):</td>'
                '<td style="padding:8px;border:1px solid #ddd;text-align:right;">'
                "\u20b9{half2:,.2f}</td>"
                "</tr>"
            ).format(half=half_gst, half2=half_gst)
        else:
            gst_breakdown = (
                "<tr>"
                '<td colspan="6" style="padding:8px;border:1px solid #ddd;text-align:right;">IGST (18%):</td>'
                '<td style="padding:8px;border:1px solid #ddd;text-align:right;">'
                "\u20b9{gst:,.2f}</td>"
                "</tr>"
            ).format(gst=total_gst)

        payment_ref = ""
        if payment_id:
            payment_ref = "<p><strong>Payment Reference:</strong> {}</p>".format(payment_id)

        customer_gstin_row = ""
        if customer_gstin:
            customer_gstin_row = "<p><strong>GSTIN:</strong> {}</p>".format(customer_gstin)

        html = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Invoice {invoice_number}</title>
<style>
    body {{ font-family: 'Helvetica', Arial, sans-serif; color: #1a1a1a; margin: 0; padding: 20px; }}
    .invoice-box {{ max-width: 800px; margin: auto; border: 1px solid #eee; padding: 30px; }}
    .header {{ display: flex; justify-content: space-between; margin-bottom: 30px; border-bottom: 3px solid #7c3aed; padding-bottom: 20px; }}
    .company {{ font-size: 20px; font-weight: bold; color: #7c3aed; }}
    table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
    th {{ background: #7c3aed; color: white; padding: 10px 8px; text-align: left; }}
    .total-row {{ background: #f3f0ff; font-weight: bold; }}
    .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; font-size: 11px; color: #666; }}
    .stamp {{ text-align: right; margin-top: 40px; }}
</style></head>
<body>
<div class="invoice-box">
    <div class="header">
        <div>
            <div class="company">{company_name}</div>
            <p style="margin:5px 0;font-size:12px;">{company_address}</p>
            <p style="margin:2px 0;font-size:12px;"><strong>GSTIN:</strong> {company_gstin}</p>
            <p style="margin:2px 0;font-size:12px;"><strong>PAN:</strong> {company_pan}</p>
        </div>
        <div style="text-align:right;">
            <h2 style="color:#7c3aed;margin:0;">TAX INVOICE</h2>
            <p style="margin:5px 0;"><strong>Invoice No:</strong> {invoice_number}</p>
            <p style="margin:5px 0;"><strong>Date:</strong> {date_str}</p>
        </div>
    </div>

    <div style="display:flex;justify-content:space-between;margin-bottom:20px;">
        <div>
            <h3 style="color:#7c3aed;margin:0 0 10px 0;">Bill To:</h3>
            <p style="margin:2px 0;"><strong>{customer_name}</strong></p>
            <p style="margin:2px 0;font-size:12px;">{customer_address}</p>
            <p style="margin:2px 0;font-size:12px;">{customer_email}</p>
            {customer_gstin_row}
        </div>
    </div>

    {payment_ref}

    <table>
        <thead>
            <tr>
                <th style="width:5%">#</th>
                <th>Description</th>
                <th style="width:10%;text-align:center;">SAC</th>
                <th style="width:12%;text-align:right;">Amount</th>
                <th style="width:8%;text-align:center;">GST</th>
                <th style="width:12%;text-align:right;">GST Amt</th>
                <th style="width:12%;text-align:right;">Total</th>
            </tr>
        </thead>
        <tbody>
            {items_html}
            <tr><td colspan="6" style="padding:8px;border:1px solid #ddd;text-align:right;"><strong>Subtotal:</strong></td>
            <td style="padding:8px;border:1px solid #ddd;text-align:right;">\u20b9{subtotal:,.2f}</td></tr>
            {gst_breakdown}
            <tr class="total-row"><td colspan="6" style="padding:10px 8px;border:1px solid #ddd;text-align:right;font-size:14px;">Grand Total:</td>
            <td style="padding:10px 8px;border:1px solid #ddd;text-align:right;font-size:14px;">\u20b9{grand_total:,.2f}</td></tr>
        </tbody>
    </table>

    <p><strong>Amount in words:</strong> {amount_words} Only</p>

    <div class="stamp">
        <p>For {company_name}</p>
        <br><br>
        <p>____________________________</p>
        <p>Authorized Signatory</p>
    </div>

    <div class="footer">
        <p>This is a computer generated invoice and does not require a physical signature.</p>
        <p>Subject to Bangalore jurisdiction. E&amp;OE.</p>
    </div>
</div>
</body></html>""".format(
            invoice_number=invoice_number,
            company_name=self.COMPANY_DETAILS["name"],
            company_address=self.COMPANY_DETAILS["address"],
            company_gstin=self.COMPANY_DETAILS["gstin"],
            company_pan=self.COMPANY_DETAILS["pan"],
            date_str=date_str,
            customer_name=customer_name,
            customer_address=customer_address,
            customer_email=customer_email,
            customer_gstin_row=customer_gstin_row,
            payment_ref=payment_ref,
            items_html=items_html,
            subtotal=subtotal,
            gst_breakdown=gst_breakdown,
            grand_total=grand_total,
            amount_words=amount_words,
        )
        return html

    def generate_receipt_html(
        self,
        receipt_number: str,
        customer_name: str,
        amount: float,
        payment_method: str,
        payment_id: str,
        description: str,
        receipt_date: Optional[datetime] = None,
    ) -> str:
        """Generate a simple payment receipt."""
        date = receipt_date or datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)
        date_str = date.strftime("%d %B %Y, %I:%M %p IST")

        html = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Receipt {receipt_number}</title>
<style>
    body {{ font-family: 'Helvetica', Arial, sans-serif; color: #1a1a1a; margin: 0; padding: 20px; }}
    .receipt {{ max-width: 500px; margin: auto; border: 1px solid #eee; padding: 30px; border-radius: 8px; }}
    .header {{ text-align: center; border-bottom: 2px solid #10b981; padding-bottom: 15px; margin-bottom: 20px; }}
    .checkmark {{ font-size: 48px; color: #10b981; }}
    .amount {{ font-size: 28px; font-weight: bold; color: #1a1a1a; text-align: center; margin: 20px 0; }}
    .detail {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f0f0f0; font-size: 14px; }}
    .footer {{ margin-top: 20px; text-align: center; font-size: 11px; color: #999; }}
</style></head>
<body>
<div class="receipt">
    <div class="header">
        <div class="checkmark">\u2713</div>
        <h2 style="margin:10px 0 5px;color:#10b981;">Payment Successful</h2>
        <p style="margin:0;color:#666;font-size:12px;">{date_str}</p>
    </div>

    <div class="amount">\u20b9{amount:,.2f}</div>

    <div class="detail"><span>Receipt No</span><strong>{receipt_number}</strong></div>
    <div class="detail"><span>Customer</span><strong>{customer_name}</strong></div>
    <div class="detail"><span>Description</span><strong>{description}</strong></div>
    <div class="detail"><span>Payment Method</span><strong>{payment_method}</strong></div>
    <div class="detail"><span>Transaction ID</span><strong>{payment_id}</strong></div>

    <div class="footer">
        <p>{company_name}</p>
        <p>This is an electronically generated receipt.</p>
    </div>
</div>
</body></html>""".format(
            receipt_number=receipt_number,
            date_str=date_str,
            amount=amount,
            customer_name=customer_name,
            description=description,
            payment_method=payment_method,
            payment_id=payment_id,
            company_name=self.COMPANY_DETAILS["name"],
        )
        return html

    def _amount_in_words(self, amount: int) -> str:
        """Convert amount to Indian English words."""
        if amount == 0:
            return "Zero Rupees"

        ones = [
            "", "One", "Two", "Three", "Four", "Five", "Six", "Seven",
            "Eight", "Nine", "Ten", "Eleven", "Twelve", "Thirteen",
            "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen",
            "Nineteen",
        ]
        tens = [
            "", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty",
            "Seventy", "Eighty", "Ninety",
        ]

        def two_digits(n):
            if n < 20:
                return ones[n]
            return tens[n // 10] + (" " + ones[n % 10] if n % 10 else "")

        def three_digits(n):
            if n >= 100:
                return ones[n // 100] + " Hundred" + (
                    " and " + two_digits(n % 100) if n % 100 else ""
                )
            return two_digits(n)

        # Indian numbering system
        parts = []
        if amount >= 10000000:
            parts.append(two_digits(amount // 10000000) + " Crore")
            amount %= 10000000
        if amount >= 100000:
            parts.append(two_digits(amount // 100000) + " Lakh")
            amount %= 100000
        if amount >= 1000:
            parts.append(two_digits(amount // 1000) + " Thousand")
            amount %= 1000
        if amount > 0:
            parts.append(three_digits(amount))

        return " ".join(parts) + " Rupees"


# Module-level singleton
invoice_service = InvoiceService()
