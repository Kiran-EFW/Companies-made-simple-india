"use client";

import { ReactNode } from "react";

export default function InvestorPortalLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Minimal header — no auth guard */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">A</span>
            </div>
            <span className="text-xl font-semibold text-gray-900">Anvils</span>
            <span className="text-sm text-gray-500 ml-2">Investor Portal</span>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8">{children}</main>

      <footer className="border-t border-gray-200 bg-white px-6 py-4 mt-12">
        <div className="max-w-6xl mx-auto text-center text-sm text-gray-500">
          Powered by Anvils — Equity & Governance Platform
        </div>
      </footer>
    </div>
  );
}
