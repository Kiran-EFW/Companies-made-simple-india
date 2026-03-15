"""Branded HTML email template service using Jinja2.

Provides consistent email styling across all notifications sent by the platform.
"""

from jinja2 import Template


# ── Base Template ────────────────────────────────────────────────────────────

_BASE_TEMPLATE = Template("""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#F1F5F9;font-family:'Segoe UI',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#F1F5F9;padding:30px 0;">
<tr><td align="center">
<table width="600" cellpadding="0" cellspacing="0" style="background:#FFFFFF;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.06);">
  <!-- Header -->
  <tr>
    <td style="background:linear-gradient(135deg,#7C3AED,#6D28D9);padding:28px 40px;text-align:center;">
      <h1 style="margin:0;color:#FFFFFF;font-size:22px;font-weight:700;letter-spacing:0.5px;">
        Anvils
      </h1>
    </td>
  </tr>
  <!-- Body -->
  <tr>
    <td style="padding:36px 40px;">
      {{ content }}
    </td>
  </tr>
  <!-- Footer -->
  <tr>
    <td style="background:#F8FAFC;padding:24px 40px;border-top:1px solid #E2E8F0;">
      <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
          <td style="text-align:center;color:#94A3B8;font-size:12px;line-height:1.6;">
            <p style="margin:0 0 8px 0;font-weight:600;color:#64748B;">Anvils</p>
            <p style="margin:0 0 4px 0;">Making company incorporation effortless</p>
            <p style="margin:12px 0 0 0;">
              <a href="https://companiesmade.in" style="color:#7C3AED;text-decoration:none;">Website</a>
              &nbsp;&middot;&nbsp;
              <a href="https://companiesmade.in/support" style="color:#7C3AED;text-decoration:none;">Support</a>
              &nbsp;&middot;&nbsp;
              <a href="https://companiesmade.in/privacy" style="color:#7C3AED;text-decoration:none;">Privacy</a>
            </p>
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>
</td></tr>
</table>
</body>
</html>""")


# ── Content Templates ────────────────────────────────────────────────────────

_WELCOME_CONTENT = Template("""
<h2 style="color:#1E293B;font-size:20px;margin:0 0 16px 0;">Welcome, {{ user_name }}!</h2>
<p style="font-size:15px;line-height:1.7;color:#475569;">
  Thank you for joining Anvils. We are here to make
  your company incorporation journey smooth and hassle-free.
</p>
<div style="background:#F5F3FF;border-radius:8px;padding:20px;margin:24px 0;">
  <h3 style="color:#7C3AED;margin:0 0 12px 0;font-size:15px;">Getting Started</h3>
  <ul style="font-size:14px;line-height:2;padding-left:20px;color:#475569;margin:0;">
    <li>Choose your entity type (Private Limited, LLP, OPC, etc.)</li>
    <li>Select a plan that fits your needs</li>
    <li>Complete payment securely via Razorpay</li>
    <li>Upload your documents and we handle the rest</li>
  </ul>
</div>
<p style="font-size:14px;line-height:1.6;color:#94A3B8;">
  Our AI-powered platform guides you through every step. If you have any
  questions, simply reply to this email.
</p>
""")


_PAYMENT_CONFIRMATION_CONTENT = Template("""
<h2 style="color:#16A34A;font-size:20px;margin:0 0 16px 0;">Payment Successful!</h2>
<p style="font-size:15px;line-height:1.7;color:#475569;">
  Hi {{ user_name }}, your payment has been received and verified.
</p>
<div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:8px;padding:20px;margin:24px 0;">
  <table width="100%" style="font-size:14px;border-collapse:collapse;">
    <tr>
      <td style="padding:8px 0;color:#64748B;">Company</td>
      <td style="padding:8px 0;text-align:right;font-weight:600;color:#1E293B;">{{ company_name }}</td>
    </tr>
    <tr>
      <td style="padding:8px 0;color:#64748B;">Amount Paid</td>
      <td style="padding:8px 0;text-align:right;font-weight:600;color:#1E293B;">Rs. {{ amount }}</td>
    </tr>
    <tr>
      <td style="padding:8px 0;color:#64748B;">Receipt No.</td>
      <td style="padding:8px 0;text-align:right;font-family:monospace;font-size:12px;color:#1E293B;">{{ receipt_no }}</td>
    </tr>
  </table>
</div>
<div style="background:#F5F3FF;border-radius:8px;padding:20px;margin:24px 0;">
  <h3 style="color:#7C3AED;margin:0 0 12px 0;font-size:15px;">What Happens Next?</h3>
  <ol style="font-size:14px;line-height:2;padding-left:20px;color:#475569;margin:0;">
    <li>Upload required documents (director KYC, address proof, etc.)</li>
    <li>Our team verifies your documents</li>
    <li>We begin your company name reservation with MCA</li>
    <li>DSC procurement and incorporation filing</li>
  </ol>
</div>
""")


_STATUS_UPDATE_CONTENT = Template("""
<h2 style="color:#1E293B;font-size:20px;margin:0 0 16px 0;">Status Update for {{ company_name }}</h2>
<p style="font-size:15px;line-height:1.7;color:#475569;">Hi {{ user_name }},</p>
<p style="font-size:15px;line-height:1.7;color:#475569;">
  Your company registration status has been updated.
</p>
<div style="background:#EFF6FF;border:1px solid #BFDBFE;border-radius:8px;padding:20px;margin:24px 0;">
  <table width="100%" style="font-size:14px;border-collapse:collapse;">
    <tr>
      <td style="padding:8px 0;color:#64748B;">Previous Status</td>
      <td style="padding:8px 0;text-align:right;color:#94A3B8;">{{ old_status }}</td>
    </tr>
    <tr>
      <td style="padding:8px 0;color:#64748B;">Current Status</td>
      <td style="padding:8px 0;text-align:right;font-weight:600;color:#7C3AED;">{{ new_status }}</td>
    </tr>
  </table>
</div>
{% if next_steps %}
<div style="background:#F5F3FF;border-radius:8px;padding:20px;margin:24px 0;">
  <h3 style="color:#7C3AED;margin:0 0 12px 0;font-size:15px;">Next Steps</h3>
  <p style="font-size:14px;line-height:1.7;color:#475569;margin:0;">{{ next_steps }}</p>
</div>
{% endif %}
<p style="font-size:14px;line-height:1.6;color:#94A3B8;">
  Log in to your dashboard to see full details.
</p>
""")


_DOCUMENT_REQUEST_CONTENT = Template("""
<h2 style="color:#1E293B;font-size:20px;margin:0 0 16px 0;">Document Required</h2>
<p style="font-size:15px;line-height:1.7;color:#475569;">Hi {{ user_name }},</p>
<p style="font-size:15px;line-height:1.7;color:#475569;">
  We need a document for your company <strong>{{ company_name }}</strong> to proceed
  with the incorporation process.
</p>
<div style="background:#FFF7ED;border:1px solid #FED7AA;border-radius:8px;padding:20px;margin:24px 0;">
  <table width="100%" style="font-size:14px;border-collapse:collapse;">
    <tr>
      <td style="padding:8px 0;color:#64748B;">Document Type</td>
      <td style="padding:8px 0;text-align:right;font-weight:600;color:#EA580C;">{{ doc_type }}</td>
    </tr>
  </table>
  {% if message %}
  <p style="font-size:14px;line-height:1.6;color:#475569;margin:12px 0 0 0;">{{ message }}</p>
  {% endif %}
</div>
<p style="font-size:14px;line-height:1.6;color:#94A3B8;">
  Please upload the document via your dashboard at the earliest.
</p>
""")


_COMPLIANCE_REMINDER_CONTENT = Template("""
<h2 style="color:#1E293B;font-size:20px;margin:0 0 16px 0;">Compliance Reminder</h2>
<p style="font-size:15px;line-height:1.7;color:#475569;">Hi {{ user_name }},</p>
<p style="font-size:15px;line-height:1.7;color:#475569;">
  This is a reminder about an upcoming compliance filing for
  <strong>{{ company_name }}</strong>.
</p>
<div style="background:{% if days_left <= 3 %}#FEF2F2;border:1px solid #FECACA{% elif days_left <= 7 %}#FFF7ED;border:1px solid #FED7AA{% else %}#F0FDF4;border:1px solid #BBF7D0{% endif %};border-radius:8px;padding:20px;margin:24px 0;">
  <table width="100%" style="font-size:14px;border-collapse:collapse;">
    <tr>
      <td style="padding:8px 0;color:#64748B;">Filing</td>
      <td style="padding:8px 0;text-align:right;font-weight:600;color:#1E293B;">{{ filing_name }}</td>
    </tr>
    <tr>
      <td style="padding:8px 0;color:#64748B;">Due Date</td>
      <td style="padding:8px 0;text-align:right;font-weight:600;color:#1E293B;">{{ due_date }}</td>
    </tr>
    <tr>
      <td style="padding:8px 0;color:#64748B;">Days Remaining</td>
      <td style="padding:8px 0;text-align:right;font-weight:700;color:{% if days_left <= 3 %}#DC2626{% elif days_left <= 7 %}#EA580C{% else %}#16A34A{% endif %};">{{ days_left }} days</td>
    </tr>
  </table>
</div>
<p style="font-size:14px;line-height:1.6;color:#94A3B8;">
  Timely filings help avoid penalties. Contact us if you need assistance.
</p>
""")


# ── Public API ───────────────────────────────────────────────────────────────

class EmailTemplateService:
    """Renders branded HTML email templates using Jinja2."""

    @staticmethod
    def _wrap(content_html: str) -> str:
        """Wrap content in the base layout template."""
        return _BASE_TEMPLATE.render(content=content_html)

    def render_welcome(self, user_name: str) -> str:
        content = _WELCOME_CONTENT.render(user_name=user_name)
        return self._wrap(content)

    def render_payment_confirmation(
        self,
        user_name: str,
        company_name: str,
        amount: str,
        receipt_no: str,
    ) -> str:
        content = _PAYMENT_CONFIRMATION_CONTENT.render(
            user_name=user_name,
            company_name=company_name,
            amount=amount,
            receipt_no=receipt_no,
        )
        return self._wrap(content)

    def render_status_update(
        self,
        user_name: str,
        company_name: str,
        old_status: str,
        new_status: str,
        next_steps: str = "",
    ) -> str:
        old_label = old_status.replace("_", " ").title()
        new_label = new_status.replace("_", " ").title()
        content = _STATUS_UPDATE_CONTENT.render(
            user_name=user_name,
            company_name=company_name,
            old_status=old_label,
            new_status=new_label,
            next_steps=next_steps,
        )
        return self._wrap(content)

    def render_document_request(
        self,
        user_name: str,
        company_name: str,
        doc_type: str,
        message: str = "",
    ) -> str:
        content = _DOCUMENT_REQUEST_CONTENT.render(
            user_name=user_name,
            company_name=company_name,
            doc_type=doc_type,
            message=message,
        )
        return self._wrap(content)

    def render_compliance_reminder(
        self,
        user_name: str,
        company_name: str,
        filing_name: str,
        due_date: str,
        days_left: int,
    ) -> str:
        content = _COMPLIANCE_REMINDER_CONTENT.render(
            user_name=user_name,
            company_name=company_name,
            filing_name=filing_name,
            due_date=due_date,
            days_left=days_left,
        )
        return self._wrap(content)


# Module-level singleton
email_template_service = EmailTemplateService()
