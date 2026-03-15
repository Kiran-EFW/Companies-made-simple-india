from src.config import get_settings

settings = get_settings()


class EmailService:
    """Email notification service using SendGrid.

    In dev mode (empty API key), logs emails to the console
    instead of sending them through SendGrid.
    """

    def __init__(self):
        self.api_key = settings.sendgrid_api_key
        self.from_email = settings.from_email
        self.from_name = settings.from_name
        self._sg = None

        if self.api_key:
            from sendgrid import SendGridAPIClient
            self._sg = SendGridAPIClient(api_key=self.api_key)

    @property
    def is_live(self) -> bool:
        return self._sg is not None

    def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send an email via SendGrid or log to console in dev mode.

        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_content: HTML body content

        Returns:
            True if sent/logged successfully, False otherwise
        """
        if not self.is_live:
            print(f"[EMAIL DEV] To: {to_email}, Subject: {subject}")
            print(f"[EMAIL DEV] Body preview: {html_content[:200]}...")
            return True

        try:
            from sendgrid.helpers.mail import Mail

            message = Mail(
                from_email=(self.from_email, self.from_name),
                to_emails=to_email,
                subject=subject,
                html_content=html_content,
            )
            response = self._sg.send(message)
            return response.status_code in (200, 201, 202)
        except Exception as e:
            print(f"[EMAIL ERROR] Failed to send email to {to_email}: {e}")
            return False

    def send_welcome_email(self, user_name: str, user_email: str) -> bool:
        """Send a welcome email after user signup.

        Args:
            user_name: The user's full name
            user_email: The user's email address

        Returns:
            True if sent successfully
        """
        subject = "Welcome to Anvils!"
        html_content = f"""
        <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #333333;">
            <div style="text-align: center; padding: 20px 0; border-bottom: 2px solid #2563EB;">
                <h1 style="color: #2563EB; margin: 0; font-size: 24px;">Anvils</h1>
            </div>

            <div style="padding: 30px 0;">
                <h2 style="color: #1E293B; font-size: 20px;">Welcome, {user_name}!</h2>
                <p style="font-size: 16px; line-height: 1.6;">
                    Thank you for joining Anvils. We are here to make
                    your company incorporation journey smooth and hassle-free.
                </p>

                <div style="background: #F8FAFC; border-radius: 8px; padding: 20px; margin: 20px 0;">
                    <h3 style="color: #2563EB; margin-top: 0; font-size: 16px;">Getting Started</h3>
                    <ul style="font-size: 14px; line-height: 1.8; padding-left: 20px;">
                        <li>Choose your entity type (Private Limited, LLP, OPC, etc.)</li>
                        <li>Select a plan that fits your needs</li>
                        <li>Complete payment securely via Razorpay</li>
                        <li>Upload your documents and we handle the rest</li>
                    </ul>
                </div>

                <p style="font-size: 14px; line-height: 1.6; color: #64748B;">
                    Our AI-powered platform guides you through every step. If you have any
                    questions, simply reply to this email.
                </p>
            </div>

            <div style="border-top: 1px solid #E2E8F0; padding: 20px 0; text-align: center; color: #94A3B8; font-size: 12px;">
                <p style="margin: 0;">Anvils</p>
                <p style="margin: 5px 0 0 0;">Making company incorporation effortless</p>
            </div>
        </div>
        """
        return self.send_email(user_email, subject, html_content)

    def send_payment_confirmation(
        self,
        user_email: str,
        user_name: str,
        company_name: str,
        amount: str,
        order_id: str,
    ) -> bool:
        """Send payment confirmation receipt.

        Args:
            user_email: Recipient email
            user_name: User's full name
            company_name: The company being incorporated
            amount: Formatted amount string (e.g. "9,999.00")
            order_id: Razorpay order ID for reference

        Returns:
            True if sent successfully
        """
        subject = f"Payment Confirmed - {company_name}"
        html_content = f"""
        <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #333333;">
            <div style="text-align: center; padding: 20px 0; border-bottom: 2px solid #2563EB;">
                <h1 style="color: #2563EB; margin: 0; font-size: 24px;">Anvils</h1>
            </div>

            <div style="padding: 30px 0;">
                <h2 style="color: #16A34A; font-size: 20px;">Payment Successful!</h2>
                <p style="font-size: 16px; line-height: 1.6;">
                    Hi {user_name}, your payment has been received and verified.
                </p>

                <div style="background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 8px; padding: 20px; margin: 20px 0;">
                    <table style="width: 100%; font-size: 14px; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px 0; color: #64748B;">Company</td>
                            <td style="padding: 8px 0; text-align: right; font-weight: 600;">{company_name}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #64748B;">Amount Paid</td>
                            <td style="padding: 8px 0; text-align: right; font-weight: 600;">Rs. {amount}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #64748B;">Order ID</td>
                            <td style="padding: 8px 0; text-align: right; font-family: monospace; font-size: 12px;">{order_id}</td>
                        </tr>
                    </table>
                </div>

                <div style="background: #F8FAFC; border-radius: 8px; padding: 20px; margin: 20px 0;">
                    <h3 style="color: #2563EB; margin-top: 0; font-size: 16px;">What Happens Next?</h3>
                    <ol style="font-size: 14px; line-height: 1.8; padding-left: 20px;">
                        <li>Upload required documents (director KYC, address proof, etc.)</li>
                        <li>Our team verifies your documents</li>
                        <li>We begin your company name reservation with MCA</li>
                        <li>DSC procurement and incorporation filing</li>
                    </ol>
                </div>

                <p style="font-size: 14px; line-height: 1.6; color: #64748B;">
                    You can track your incorporation progress in real-time on your dashboard.
                </p>
            </div>

            <div style="border-top: 1px solid #E2E8F0; padding: 20px 0; text-align: center; color: #94A3B8; font-size: 12px;">
                <p style="margin: 0;">Anvils</p>
                <p style="margin: 5px 0 0 0;">This is an automated payment receipt. Please keep it for your records.</p>
            </div>
        </div>
        """
        return self.send_email(user_email, subject, html_content)

    def send_status_update(
        self,
        user_email: str,
        user_name: str,
        company_name: str,
        old_status: str,
        new_status: str,
        message: str,
    ) -> bool:
        """Send a company status change notification.

        Args:
            user_email: Recipient email
            user_name: User's full name
            company_name: The company name
            old_status: Previous status value
            new_status: New status value
            message: Human-readable message about the status change

        Returns:
            True if sent successfully
        """
        # Format status labels for display
        old_label = old_status.replace("_", " ").title()
        new_label = new_status.replace("_", " ").title()

        subject = f"Status Update: {company_name} - {new_label}"
        html_content = f"""
        <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #333333;">
            <div style="text-align: center; padding: 20px 0; border-bottom: 2px solid #2563EB;">
                <h1 style="color: #2563EB; margin: 0; font-size: 24px;">Anvils</h1>
            </div>

            <div style="padding: 30px 0;">
                <h2 style="color: #1E293B; font-size: 20px;">Status Update for {company_name}</h2>
                <p style="font-size: 16px; line-height: 1.6;">Hi {user_name},</p>
                <p style="font-size: 16px; line-height: 1.6;">{message}</p>

                <div style="background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 8px; padding: 20px; margin: 20px 0;">
                    <table style="width: 100%; font-size: 14px; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px 0; color: #64748B;">Previous Status</td>
                            <td style="padding: 8px 0; text-align: right; color: #94A3B8;">{old_label}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px 0; color: #64748B;">Current Status</td>
                            <td style="padding: 8px 0; text-align: right; font-weight: 600; color: #2563EB;">{new_label}</td>
                        </tr>
                    </table>
                </div>

                <p style="font-size: 14px; line-height: 1.6; color: #64748B;">
                    Log in to your dashboard to see full details and next steps.
                </p>
            </div>

            <div style="border-top: 1px solid #E2E8F0; padding: 20px 0; text-align: center; color: #94A3B8; font-size: 12px;">
                <p style="margin: 0;">Anvils</p>
                <p style="margin: 5px 0 0 0;">Automated status notification</p>
            </div>
        </div>
        """
        return self.send_email(user_email, subject, html_content)


# Module-level singleton
email_service = EmailService()
