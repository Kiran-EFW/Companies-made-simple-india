import { Metadata } from "next";
import Header from "@/components/header";
import Footer from "@/components/footer";
import ChatWidget from "@/components/chat-widget";

export const metadata: Metadata = {
  title: "Terms of Service — Anvils",
  description:
    "Terms and conditions governing your use of the Anvils platform.",
};

export default function TermsOfServicePage() {
  return (
    <div className="glow-bg">
      <Header />

      <div className="max-w-3xl mx-auto px-6 py-16">
        <h1
          className="text-3xl font-extrabold mb-2 text-[var(--color-text-primary)]"
          style={{ fontFamily: "var(--font-display)" }}
        >
          Terms of Service
        </h1>
        <p className="text-sm text-[var(--color-text-muted)] mb-10">
          Last updated: 23 March 2026
        </p>

        <div className="space-y-8 text-sm leading-relaxed text-[var(--color-text-secondary)]">
          <section>
            <h2 className="text-lg font-bold text-[var(--color-text-primary)] mb-3">
              1. Acceptance of Terms
            </h2>
            <p>
              By accessing or using Anvils (&ldquo;the Platform&rdquo;), you agree to be bound by these Terms of Service. If you are using the Platform on behalf of a company, you represent that you have authority to bind that entity to these terms.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-[var(--color-text-primary)] mb-3">
              2. Description of Service
            </h2>
            <p className="mb-3">Anvils provides a software platform for Indian companies that includes:</p>
            <ul className="list-disc pl-5 space-y-1.5">
              <li>Company incorporation assistance and filing management</li>
              <li>Cap table management and equity tracking</li>
              <li>ESOP plan creation and grant management</li>
              <li>Compliance calendar and deadline tracking</li>
              <li>Fundraising round management and investor portal</li>
              <li>Document management and e-signatures</li>
              <li>Services marketplace connecting companies with professional CAs/CSs</li>
              <li>CA/CS multi-client management dashboard</li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-bold text-[var(--color-text-primary)] mb-3">
              3. User Accounts
            </h2>
            <ul className="list-disc pl-5 space-y-1.5">
              <li>You must provide accurate and complete information when creating an account.</li>
              <li>You are responsible for maintaining the security of your account credentials.</li>
              <li>You must notify us immediately of any unauthorized access to your account.</li>
              <li>One person or entity may maintain multiple accounts only for managing separate companies.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-bold text-[var(--color-text-primary)] mb-3">
              4. Subscription Plans & Payments
            </h2>
            <ul className="list-disc pl-5 space-y-1.5">
              <li>Free plan features are available without payment. Paid plans (Growth, Scale) are billed monthly or annually.</li>
              <li>Incorporation fees are one-time payments that include government fees, stamp duty, and platform fees as itemized during checkout.</li>
              <li>Marketplace service fees are charged when you place an order. The breakdown between professional fees and platform fees is displayed before purchase.</li>
              <li>All payments are processed through Razorpay and are subject to their terms.</li>
              <li>Subscription renewals are automatic. You may cancel at any time; access continues until the end of the current billing period.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-bold text-[var(--color-text-primary)] mb-3">
              5. Marketplace Terms
            </h2>
            <p className="mb-3">
              The Anvils Services Marketplace connects companies with verified CA/CS/CMA professionals. Additional terms apply:
            </p>
            <ul className="list-disc pl-5 space-y-1.5">
              <li>
                <strong>For clients:</strong> Services are fulfilled by independent professionals, not by Anvils. Anvils facilitates the connection and provides quality oversight but does not provide professional services directly.
              </li>
              <li>
                <strong>For partners:</strong> Partners receive 80% of the service fee. Anvils deducts TDS at 10% under Section 194J on the partner&apos;s share. Partners are responsible for their own GST compliance.
              </li>
              <li>
                <strong>Quality assurance:</strong> All deliverables are reviewed before release to clients. Partners who consistently receive low ratings may have their marketplace access suspended.
              </li>
              <li>
                <strong>Disputes:</strong> Service disputes should be reported within 7 days of delivery. Anvils will mediate between the client and partner in good faith.
              </li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-bold text-[var(--color-text-primary)] mb-3">
              6. Data Ownership
            </h2>
            <ul className="list-disc pl-5 space-y-1.5">
              <li>You retain ownership of all data you upload or enter into the Platform.</li>
              <li>You grant Anvils a limited license to process your data as necessary to provide the service.</li>
              <li>Company data (cap table, compliance records, documents) belongs to the company and its authorized users.</li>
              <li>You may export your data at any time through the Platform&apos;s export features.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-bold text-[var(--color-text-primary)] mb-3">
              7. Acceptable Use
            </h2>
            <p className="mb-3">You agree not to:</p>
            <ul className="list-disc pl-5 space-y-1.5">
              <li>Use the Platform for any unlawful purpose or to facilitate fraud.</li>
              <li>Upload false or misleading company information or documents.</li>
              <li>Attempt to access data belonging to other companies or users.</li>
              <li>Reverse engineer, decompile, or attempt to extract the source code of the Platform.</li>
              <li>Resell or redistribute the Platform without written permission.</li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-bold text-[var(--color-text-primary)] mb-3">
              8. Disclaimers
            </h2>
            <ul className="list-disc pl-5 space-y-1.5">
              <li>
                <strong>Not legal/financial advice:</strong> Anvils is a software tool. Information provided through the Platform (compliance calendars, TDS calculations, entity comparisons) is for reference only and does not constitute professional legal, tax, or financial advice.
              </li>
              <li>
                <strong>Compliance tracking:</strong> While we auto-generate compliance tasks based on entity type and applicable regulations, you are ultimately responsible for ensuring all filings are made correctly and on time.
              </li>
              <li>
                <strong>Incorporation:</strong> Anvils facilitates the incorporation process but final approval rests with the relevant government authorities (MCA, state registrars).
              </li>
            </ul>
          </section>

          <section>
            <h2 className="text-lg font-bold text-[var(--color-text-primary)] mb-3">
              9. Limitation of Liability
            </h2>
            <p>
              To the maximum extent permitted by law, Anvils shall not be liable for any indirect, incidental, special, consequential, or punitive damages, including loss of profits, data, or business opportunities, arising from your use of the Platform. Our total liability shall not exceed the amount paid by you to Anvils in the 12 months preceding the claim.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-[var(--color-text-primary)] mb-3">
              10. Termination
            </h2>
            <p>
              Either party may terminate this agreement at any time. Upon termination, your access to paid features will end, but you may export your data for 30 days after termination. We may suspend or terminate accounts that violate these terms without notice.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-[var(--color-text-primary)] mb-3">
              11. Governing Law
            </h2>
            <p>
              These terms are governed by the laws of India. Any disputes arising from these terms shall be subject to the exclusive jurisdiction of the courts in Bengaluru, Karnataka.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-[var(--color-text-primary)] mb-3">
              12. Changes to Terms
            </h2>
            <p>
              We may modify these terms at any time. We will notify registered users of material changes via email at least 14 days before they take effect. Continued use of the Platform after changes take effect constitutes acceptance.
            </p>
          </section>

          <section>
            <h2 className="text-lg font-bold text-[var(--color-text-primary)] mb-3">
              13. Contact
            </h2>
            <p>
              For questions about these terms, contact us at{" "}
              <a href="mailto:legal@anvils.in" className="text-purple-600 hover:underline">
                legal@anvils.in
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
