import { Metadata } from "next";
import Header from "@/components/header";
import Footer from "@/components/footer";
import ChatWidget from "@/components/chat-widget";

export const metadata: Metadata = {
  title: "Privacy Policy — Anvils",
  description:
    "Learn how Anvils collects, uses, and protects your personal and company data.",
};

export default function PrivacyPolicyPage() {
  return (
    <div className="glow-bg">
      <Header />

      <div className="max-w-3xl mx-auto px-6 py-16">
        <h1
          className="text-3xl font-extrabold mb-2 text-[var(--color-text-primary)]"
          style={{ fontFamily: "var(--font-display)" }}
        >
          Privacy Policy
        </h1>
        <p className="text-sm text-[var(--color-text-muted)] mb-10">
          Last updated: 23 March 2026
        </p>

        <div className="space-y-8 text-sm leading-relaxed text-[var(--color-text-secondary)]">
          <section>
            <h2 className="text-lg font-bold text-[var(--color-text-primary)] mb-3">
              1. Information We Collect
            </h2>
            <p className="mb-3">
              When you use Anvils, we collect information that you provide directly, information generated through your use of the platform, and information from third-party sources where applicable.
            </p>
            <ul className="list-disc pl-5 space-y-1.5">
              <li>
                <strong>Account information:</strong> Name, email address, phone number, and professional credentials (for CA/CS/CMA users).
              </li>
              <li>
                <strong>Company information:</strong> Entity name, type, CIN/LLPIN, registered address, director/partner details, and incorporation documents.
              </li>
              <li>
                <strong>Financial information:</strong> Cap table data, share transactions, valuation details, and fundraising round information as entered by you.
              </li>
              <li>
                <strong>Identity documents:</strong> PAN, Aadhaar (for e-KYC during incorporation), DIN details, and DSC information. These are processed securely and masked in logs.
              </li>
              <li>
                <strong>Usage data:</strong> Pages visited, features used, timestamps, IP addresses, browser type, and device information.
              </li>
              <li>
                <strong>Payment information:</strong> Processed by Razorpay. We do not store your full card or bank account details.
              </li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-bold text-[var(--color-text-primary)] mb-3">
              2. How We Use Your Information
            </h2>
            <ul className="list-disc pl-5 space-y-1.5">
              <li>To provide and operate the Anvils platform, including company incorporation, compliance tracking, cap table management, and marketplace services.</li>
              <li>To generate compliance calendars, auto-track regulatory deadlines, and send reminders.</li>
              <li>To facilitate secure investor portal access via token-based links.</li>
              <li>To process payments for incorporation fees, subscription plans, and marketplace services.</li>
              <li>To match service requests with partner CAs/CSs in the marketplace.</li>
              <li>To improve our platform, fix bugs, and develop new features.</li>
              <li>To communicate with you about your account, service updates, and compliance-related notifications.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-bold text-[var(--color-text-primary)] mb-3">
              3. Data Sharing
            </h2>
            <p className="mb-3">We do not sell your personal data. We share information only in the following circumstances:</p>
            <ul className="list-disc pl-5 space-y-1.5">
              <li>
                <strong>With your designated CA/CS:</strong> When you assign a professional to your company, they can access your compliance data, documents, and filing status.
              </li>
              <li>
                <strong>Marketplace fulfillment:</strong> When you order a service, relevant order details are shared with the assigned partner for fulfillment.
              </li>
              <li>
                <strong>Investor portal:</strong> Information you explicitly choose to share via investor portal links.
              </li>
              <li>
                <strong>Payment processors:</strong> Razorpay processes your payments under their own privacy policy.
              </li>
              <li>
                <strong>Legal requirements:</strong> If required by law, regulation, or legal process.
              </li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-bold text-[var(--color-text-primary)] mb-3">
              4. Data Security
            </h2>
            <ul className="list-disc pl-5 space-y-1.5">
              <li>Data is encrypted in transit (TLS) and at rest.</li>
              <li>Role-based access controls ensure users only access data they are authorized to see.</li>
              <li>Full audit logging with IP tracking for all sensitive actions.</li>
              <li>Sensitive identifiers (Aadhaar, PAN) are masked in application logs.</li>
              <li>Token-based investor portal access with optional OTP verification.</li>
              <li>Regular security reviews and dependency audits.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-bold text-[var(--color-text-primary)] mb-3">
              5. Data Retention
            </h2>
            <p>
              We retain your data for as long as your account is active or as needed to provide services. Company compliance records are retained in accordance with applicable Indian laws (Companies Act, Income Tax Act). You may request deletion of your personal data by contacting us, subject to legal retention requirements.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-[var(--color-text-primary)] mb-3">
              6. Your Rights
            </h2>
            <ul className="list-disc pl-5 space-y-1.5">
              <li>Access and download your personal data.</li>
              <li>Correct inaccurate information in your profile.</li>
              <li>Request deletion of your account and personal data (subject to legal requirements).</li>
              <li>Withdraw consent for optional communications.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-bold text-[var(--color-text-primary)] mb-3">
              7. Cookies
            </h2>
            <p>
              We use essential cookies for authentication and session management. We use analytics cookies to understand how the platform is used. You can control cookie preferences in your browser settings.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-[var(--color-text-primary)] mb-3">
              8. Changes to This Policy
            </h2>
            <p>
              We may update this privacy policy from time to time. We will notify registered users of material changes via email or in-app notification.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-[var(--color-text-primary)] mb-3">
              9. Contact Us
            </h2>
            <p>
              If you have questions about this privacy policy or your data, please contact us at{" "}
              <a href="mailto:privacy@anvils.in" className="text-purple-600 hover:underline">
                privacy@anvils.in
              </a>{" "}
              or through our{" "}
              <a href="/contact" className="text-purple-600 hover:underline">
                contact page
              </a>
              .
            </p>
          </section>
        </div>
      </div>

      <Footer />
      <ChatWidget />
    </div>
  );
}
