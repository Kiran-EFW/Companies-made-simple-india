# Anvils Marketplace — Legal Structure

## Why This Document Exists

Anvils operates a services marketplace where Chartered Accountants (CAs), Company Secretaries (CSs), and other professionals fulfill compliance and regulatory services for companies on the platform. The legal structure of this marketplace must be carefully designed to comply with:

1. **CA Act, 1949** — specifically First Schedule, Part I, Clauses 2 and 6
2. **CS Act, 1980** — similar professional conduct restrictions
3. **Income Tax Act, 1961** — TDS obligations on service payments
4. **GST Act, 2017** — input service classification and invoicing
5. **Indian Contract Act, 1872** — independent contractor vs employment distinction

---

## The Regulatory Constraints

### ICAI Clause 2 — No Fee Sharing with Non-Members

> *"A Chartered Accountant in practice shall be deemed to be guilty of professional misconduct if he pays or allows or agrees to pay or allow, directly or indirectly, any share, commission or brokerage in the fees or profits of his professional business, to any person other than a member of the Institute."*

**What this means for Anvils:**

- A CA **cannot** pay Anvils a commission, referral fee, or share of their professional fees
- A CA **cannot** receive a commission from Anvils for bringing clients
- The word "commission" itself is not the issue — the underlying arrangement of fee-sharing with a non-ICAI-member is what is prohibited

### ICAI Clause 6 — No Solicitation

> *"A Chartered Accountant in practice shall be deemed to be guilty of professional misconduct if he solicits clients or professional work by advertisement or by personal communication or interview or by any other means."*

**What this means for Anvils:**

- CAs cannot use Anvils as an advertising platform in a way that constitutes solicitation
- CAs are listed as "fulfillment partners" — they do not advertise or solicit on the platform
- Anvils assigns work to partners based on availability, rating, and specialization — this is not solicitation by the CA

### CS Act Equivalent

The Institute of Company Secretaries of India (ICSI) has similar conduct rules. Company Secretaries face equivalent restrictions on fee-sharing and solicitation.

---

## The Legal Model: Anvils as Service Provider

### How It Works

```
Client (Company) → Pays Anvils → Anvils is the Service Provider
                                     ↓
                              Anvils engages a Partner Professional
                              (CA/CS/Auditor) as a fulfillment partner
                                     ↓
                              Anvils pays the partner a fulfillment fee
                              for the work delivered
```

### Key Legal Positions

| Element | Structure | Why It Works |
|---------|-----------|-------------|
| **Who is the service provider?** | Anvils India Private Limited | Client contracts with Anvils, not with the CA directly |
| **Who does the client pay?** | Anvils | Single invoice from Anvils to client |
| **Who pays the CA?** | Anvils | Anvils pays the CA a fulfillment fee for work delivered |
| **What is the CA's role?** | Independent fulfillment partner | Not an employee, not a sub-contractor in the traditional sense |
| **What is the revenue to Anvils?** | Platform service margin (difference between client price and fulfillment fee) | Anvils is not "sharing fees" — Anvils is retaining its own service margin |
| **Does the CA share fees with Anvils?** | No | The CA receives a fulfillment fee from Anvils. The CA does not pay Anvils anything |
| **Does Anvils share fees with the CA?** | No | Anvils pays the CA for work done, like any service engagement |

### Why This Does Not Violate Clause 2

The prohibition is on a CA paying/sharing their professional fees with a non-member. In this structure:

1. **The CA does not have professional fees to share** — Anvils is the service provider, not the CA. The client pays Anvils.
2. **The CA receives payment from Anvils** — this is a fulfillment fee for services rendered, not a "share" of anything.
3. **Anvils retains a margin** — this is Anvils' own revenue from its own client. No CA fees are being "shared."

This is the same legal structure used by:
- **Vakilsearch** — India's largest legal services platform. CAs and lawyers are "experts on the panel." Client pays Vakilsearch.
- **IndiaFilings** — Same model. Client pays IndiaFilings. CAs deliver the work.
- **ClearTax** — GST filing and compliance. Client pays ClearTax. CAs fulfill.
- **LegalRaasta** — Same model.

All of these platforms have operated for 8-10+ years without ICAI enforcement action, establishing strong market precedent.

---

## Money Flow

### For a Marketplace Service (e.g., Annual ROC Filing)

```
Step 1: Company orders "Annual ROC Filing" on Anvils for Rs 7,999

Step 2: Anvils issues invoice to Company for Rs 7,999 + GST
        - Anvils is the service provider on the invoice
        - GSTIN is Anvils' GSTIN
        - SAC code: 998231 (Legal and accounting services)

Step 3: Anvils assigns the filing to a Partner CA

Step 4: Partner CA completes the ROC filing (AOC-4 + MGT-7)

Step 5: Company confirms delivery / Anvils QA team verifies

Step 6: Anvils pays Partner CA a fulfillment fee of Rs 6,399
        - Anvils issues a payment advice / debit note
        - Partner CA issues their own invoice to Anvils for Rs 6,399 + GST
        - Anvils claims GST input credit on this invoice

Step 7: Anvils retains Rs 1,600 as platform service margin (20%)
```

### Tax Treatment

| Transaction | From | To | Amount | GST | TDS |
|-------------|------|-----|--------|-----|-----|
| Service fee | Company | Anvils | Rs 7,999 | 18% (Rs 1,440) | None |
| Fulfillment fee | Anvils | Partner CA | Rs 6,399 | 18% (Rs 1,152) | Sec 194J @ 10% (Rs 640) |

**Anvils' GST position:**
- Output GST collected: Rs 1,440
- Input GST credit (from CA invoice): Rs 1,152
- Net GST payable: Rs 288

**TDS obligation:**
- Anvils deducts TDS under Section 194J (professional/technical fees) at 10% on the fulfillment fee
- This is standard for any company paying a CA for professional services
- Anvils files quarterly TDS returns (Form 26Q) and issues Form 16A to partner CAs

---

## Contractual Framework

### Agreement 1: Anvils ↔ Client (Terms of Service)

The client agrees to:
- Anvils as the service provider for all marketplace services
- Anvils' right to engage qualified professionals to fulfill services
- Payment terms (advance payment before service initiation)
- Service delivery timelines (SLA)
- Dispute resolution through Anvils (not directly with the CA)

This is already covered in Anvils' Terms of Service.

### Agreement 2: Anvils ↔ Partner Professional (Partner Agreement)

See [CA Partner Agreement](ca-partner-agreement.md) for the full template.

Key terms:
- Partner is an independent professional, not an employee
- Partner receives a fulfillment fee per service delivered
- Partner does not have a direct client relationship (Anvils is the service provider)
- Partner must maintain professional qualifications (valid ICAI membership, etc.)
- Quality standards and SLA requirements
- Confidentiality and data protection
- Non-solicitation of Anvils clients (for direct engagement outside the platform)
- Termination provisions

### No Agreement Needed: CA ↔ Client

There is no direct contractual relationship between the partner CA and the client company. The client's contract is with Anvils. This is intentional and critical to the legal structure.

**Exception — Statutory Audit:** For statutory audits, the auditor must have a direct appointment by the company (required under Companies Act, Section 139). In this case, Anvils facilitates the introduction and the company directly appoints the auditor. Anvils does not intermediate the audit engagement. The marketplace fee for audit facilitation covers the matchmaking and administrative coordination, not the audit itself.

---

## Statutory Audit — Special Handling

Statutory audit has unique legal requirements that differ from other marketplace services:

| Requirement | Impact on Anvils Model |
|-------------|----------------------|
| Auditor must be appointed by the company in AGM (Sec 139) | Anvils facilitates introduction; company appoints directly |
| Auditor must be independent (Sec 141) | Anvils ensures the auditor is not the same firm handling bookkeeping/tax |
| Audit fees are between the company and auditor | Anvils charges a facilitation/matchmaking fee, not the audit fee |
| Auditor reports to shareholders, not management | No Anvils involvement in audit process or reporting |

For statutory audit, Anvils acts as a **matchmaking platform**, not a service provider. The facilitation fee covers:
- Matching the company with qualified auditors based on entity type, size, and industry
- Coordinating the introduction
- Providing the auditor with access to the company's data room (with company's permission)

---

## Professional Independence Safeguards

The marketplace enforces these independence rules:

1. **Bookkeeping ≠ Audit:** The same CA firm cannot be assigned both bookkeeping/tax services and statutory audit for the same company
2. **Rotation tracking:** For listed companies and specified companies, auditor rotation requirements are tracked
3. **Conflict of interest:** Partners self-declare conflicts; Anvils verifies against assignment history

---

## Risk Mitigation

### Risk 1: ICAI Challenges the Model

**Probability:** Low (5-10%). Vakilsearch, IndiaFilings, and ClearTax have operated this model for 8-10+ years without ICAI action.

**Mitigation:**
- Legal opinion from a practicing CA (to be obtained before launch)
- Contractual structure explicitly avoids fee-sharing language
- CAs are not paying Anvils — Anvils is paying CAs
- Partner CA's invoice is for "professional services rendered" — standard billing

### Risk 2: Partner CA Claims Employment

**Probability:** Very low. CAs are established professionals with their own practices.

**Mitigation:**
- Partner Agreement explicitly states independent contractor status
- No exclusivity — partners can (and do) serve their own clients independently
- No fixed hours, no office requirement, no tools provided
- Payment is per-service, not per-hour or per-month

### Risk 3: Client Disputes — Who Is Liable?

**Structure:** Anvils is liable to the client (as the service provider). Anvils has recourse against the partner CA under the Partner Agreement.

**Mitigation:**
- Quality checks before delivery confirmation
- Escrow-style payment (partner paid only after delivery confirmed)
- Partner performance tracking and rating system
- Removal of underperforming partners

---

## Terminology Guide

Use these terms consistently across all Anvils materials:

| Use This | Not This | Why |
|----------|----------|-----|
| Platform service margin | Commission | "Commission" implies fee-sharing, which triggers ICAI Clause 2 concerns |
| Fulfillment fee | Revenue share | "Revenue share" implies the CA is sharing their revenue |
| Partner professional / Fulfillment partner | Agent / Broker | "Agent/broker" implies intermediation and fee-sharing |
| Service margin | Markup | "Markup" implies Anvils is marking up the CA's fee |
| Platform fee | Referral fee | "Referral fee" is explicitly prohibited under Clause 2 |
| Anvils is the service provider | Anvils connects you with a CA | "Connects" implies intermediation, not service provision |

---

## Summary

Anvils' marketplace is legally structured as a **service provider model**, not an intermediary or referral platform. The client's contract is with Anvils. Anvils engages qualified professionals to fulfill the work and pays them a fulfillment fee. Anvils retains a platform service margin as its revenue. This structure is:

1. **ICAI-compliant** — no CA is sharing fees with a non-member
2. **Market-proven** — identical to Vakilsearch, IndiaFilings, ClearTax
3. **Tax-efficient** — proper GST input credit chain, TDS under 194J
4. **Scalable** — adding more partners does not change the legal structure
5. **Client-protective** — single point of accountability (Anvils)
