"use client";

import { useState } from "react";
import Header from "@/components/header";
import Footer from "@/components/footer";
import ChatWidget from "@/components/chat-widget";
import CTASection from "@/components/marketing/cta-section";
import { Mail, MessageSquare, Briefcase, Send } from "lucide-react";

const SUBJECTS = [
  "General Inquiry",
  "Sales & Pricing",
  "Technical Support",
  "CA/CS Partnership",
  "Investor Access",
  "Feedback",
];

export default function ContactPage() {
  const [form, setForm] = useState({
    name: "",
    email: "",
    subject: SUBJECTS[0],
    message: "",
  });
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // In production, this would call the backend API
    setSubmitted(true);
  };

  return (
    <div className="glow-bg">
      <Header />

      {/* ── Hero ── */}
      <section className="relative z-10 max-w-7xl mx-auto px-6 pt-20 pb-12 text-center">
        <div className="animate-fade-in-up max-w-3xl mx-auto">
          <h1
            className="text-4xl md:text-5xl font-extrabold leading-tight mb-4 text-[var(--color-text-primary)]"
            style={{ fontFamily: "var(--font-display)" }}
          >
            Get in <span className="gradient-text">touch</span>
          </h1>
          <p className="text-lg text-[var(--color-text-secondary)] leading-relaxed">
            Have a question, partnership inquiry, or feedback? We&apos;d love to
            hear from you.
          </p>
        </div>
      </section>

      {/* ── Contact Options + Form ── */}
      <section className="py-12 pb-20">
        <div className="max-w-5xl mx-auto px-6">
          <div className="grid md:grid-cols-5 gap-8">
            {/* Left: Contact Methods */}
            <div className="md:col-span-2 space-y-6">
              <div className="card-static p-6">
                <div className="w-10 h-10 rounded-xl bg-purple-50 flex items-center justify-center mb-3">
                  <Mail className="w-5 h-5 text-purple-600" />
                </div>
                <h3 className="text-base font-bold text-[var(--color-text-primary)] mb-1">
                  Email
                </h3>
                <p className="text-sm text-[var(--color-text-secondary)] mb-2">
                  For general inquiries and support.
                </p>
                <a
                  href="mailto:hello@anvils.in"
                  className="text-sm font-semibold text-purple-600 hover:underline"
                >
                  hello@anvils.in
                </a>
              </div>

              <div className="card-static p-6">
                <div className="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center mb-3">
                  <MessageSquare className="w-5 h-5 text-blue-600" />
                </div>
                <h3 className="text-base font-bold text-[var(--color-text-primary)] mb-1">
                  Live Chat
                </h3>
                <p className="text-sm text-[var(--color-text-secondary)] mb-2">
                  Use the chat widget in the bottom-right corner for quick help.
                </p>
                <span className="text-sm text-[var(--color-text-muted)]">
                  Available on all pages
                </span>
              </div>

              <div className="card-static p-6">
                <div className="w-10 h-10 rounded-xl bg-emerald-50 flex items-center justify-center mb-3">
                  <Briefcase className="w-5 h-5 text-emerald-600" />
                </div>
                <h3 className="text-base font-bold text-[var(--color-text-primary)] mb-1">
                  CA/CS Partnership
                </h3>
                <p className="text-sm text-[var(--color-text-secondary)] mb-2">
                  Interested in joining our marketplace as a service provider?
                </p>
                <a
                  href="mailto:partners@anvils.in"
                  className="text-sm font-semibold text-emerald-600 hover:underline"
                >
                  partners@anvils.in
                </a>
              </div>
            </div>

            {/* Right: Contact Form */}
            <div className="md:col-span-3">
              <div className="card-static p-6 md:p-8">
                {submitted ? (
                  <div className="text-center py-12">
                    <div className="w-14 h-14 rounded-full bg-emerald-50 flex items-center justify-center mx-auto mb-4">
                      <Send className="w-6 h-6 text-emerald-600" />
                    </div>
                    <h3
                      className="text-xl font-bold text-[var(--color-text-primary)] mb-2"
                      style={{ fontFamily: "var(--font-display)" }}
                    >
                      Message sent
                    </h3>
                    <p className="text-sm text-[var(--color-text-secondary)]">
                      We&apos;ll get back to you within 24 hours.
                    </p>
                  </div>
                ) : (
                  <form onSubmit={handleSubmit} className="space-y-5">
                    <div>
                      <label className="block text-sm font-medium text-[var(--color-text-primary)] mb-1.5">
                        Name
                      </label>
                      <input
                        type="text"
                        required
                        value={form.name}
                        onChange={(e) =>
                          setForm({ ...form, name: e.target.value })
                        }
                        className="input-field"
                        placeholder="Your name"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-[var(--color-text-primary)] mb-1.5">
                        Email
                      </label>
                      <input
                        type="email"
                        required
                        value={form.email}
                        onChange={(e) =>
                          setForm({ ...form, email: e.target.value })
                        }
                        className="input-field"
                        placeholder="you@company.com"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-[var(--color-text-primary)] mb-1.5">
                        Subject
                      </label>
                      <select
                        value={form.subject}
                        onChange={(e) =>
                          setForm({ ...form, subject: e.target.value })
                        }
                        className="input-field"
                      >
                        {SUBJECTS.map((s) => (
                          <option key={s} value={s}>
                            {s}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-[var(--color-text-primary)] mb-1.5">
                        Message
                      </label>
                      <textarea
                        required
                        rows={5}
                        value={form.message}
                        onChange={(e) =>
                          setForm({ ...form, message: e.target.value })
                        }
                        className="input-field resize-none"
                        placeholder="How can we help?"
                      />
                    </div>
                    <button type="submit" className="btn-primary w-full">
                      Send Message
                    </button>
                  </form>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>

      <Footer />
      <ChatWidget />
    </div>
  );
}
