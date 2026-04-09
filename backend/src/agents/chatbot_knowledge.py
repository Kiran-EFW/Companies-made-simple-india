"""
Chatbot knowledge base for Indian company incorporation and compliance.

This module contains structured FAQ content used as context for the chatbot
agent, covering company types, incorporation process, compliance, costs,
and common questions founders have.
"""

KNOWLEDGE_BASE = """
================================================================================
COMPANIES MADE SIMPLE INDIA -- KNOWLEDGE BASE
================================================================================

## 1. TYPES OF COMPANIES IN INDIA

### Private Limited Company (Pvt Ltd)
A Private Limited Company is the most popular structure for startups and growing
businesses in India. It is a separate legal entity with limited liability
protection for its shareholders.

Key features:
- Minimum 2 directors and 2 shareholders (can be the same persons)
- Maximum 200 shareholders
- Cannot offer shares to the public
- "Private Limited" suffix is mandatory in the company name
- Perpetual succession -- the company continues to exist regardless of changes
  in ownership
- Easier to raise funding from VCs and angel investors
- Best suited for: tech startups, funded businesses, companies planning to scale

### One Person Company (OPC)
An OPC allows a single entrepreneur to operate a corporate entity with limited
liability, without needing a partner or co-founder.

Key features:
- Only 1 shareholder and 1 director required (can be the same person)
- Must nominate a nominee director in case of incapacity or death
- Annual turnover must not exceed Rs 2 crore (otherwise must convert to Pvt Ltd)
- Paid-up capital must not exceed Rs 50 lakh
- Cannot carry out Non-Banking Financial Investment activities
- Best suited for: solo founders, freelancers wanting corporate structure,
  small businesses run by a single person

### Limited Liability Partnership (LLP)
An LLP combines the flexibility of a partnership with the limited liability of
a company. It is governed by the LLP Act, 2008.

Key features:
- Minimum 2 designated partners required (no maximum limit)
- At least one partner must be an Indian resident
- No minimum capital requirement
- Partners' liability is limited to their agreed contribution
- Lower compliance burden compared to Pvt Ltd (no mandatory audit if turnover
  < Rs 40 lakh and capital < Rs 25 lakh)
- Cannot raise equity funding (VCs typically do not invest in LLPs)
- Best suited for: professional services firms, consulting businesses,
  small businesses with multiple partners who want limited liability

### Section 8 Company (Non-Profit)
A Section 8 Company is formed for promoting commerce, art, science, sports,
education, research, social welfare, religion, charity, protection of the
environment, or any other charitable purpose.

Key features:
- Profits must be applied solely towards the objects of the company
- No dividend distribution to members
- Need a licence from the Central Government (MCA) before incorporation
- Exempt from using "Limited" or "Private Limited" in the name
- Tax exemptions available under Sections 12A and 80G of the Income Tax Act
- Best suited for: NGOs, charitable trusts, foundations, social enterprises

### Sole Proprietorship
The simplest business structure where a single individual owns and operates
the business. Not a separate legal entity.

Key features:
- No formal registration required with MCA (register under Shops & Establishments
  Act or get GST/MSME registration)
- Owner has unlimited personal liability for all business debts
- Easiest and cheapest to set up
- No separate PAN -- uses the proprietor's personal PAN
- Cannot raise external equity funding
- Best suited for: very small local businesses, initial testing of a business
  idea, freelancers who do not need corporate structure

### How to Choose the Right Entity Type
- Planning to raise VC/angel funding? -> Private Limited Company
- Solo founder with small-scale operations? -> OPC
- Professional services with partners? -> LLP
- Social or charitable purpose? -> Section 8
- Testing a small business idea? -> Sole Proprietorship


## 2. INCORPORATION PROCESS OVERVIEW

### Documents Needed for Incorporation (Pvt Ltd / OPC)
For each director/subscriber:
- PAN Card (mandatory for Indian nationals)
- Aadhaar Card
- Passport-size photograph (recent, white background)
- Address proof (Aadhaar / Voter ID / Passport / Driving License)
- Proof of residence (latest utility bill, bank statement, or mobile bill -- not
  older than 2 months)
- Digital Signature Certificate (DSC) -- Class 3

For the registered office:
- Utility bill of the proposed registered office (not older than 2 months)
- NOC (No Objection Certificate) from the property owner
- Rent agreement (if rented)
- Proof of ownership (if owned)

### Steps to Incorporate a Private Limited Company
1. Obtain DSC for all directors
2. Reserve company name via RUN (Reserve Unique Name) on MCA portal
3. Draft MOA (Memorandum of Association) and AOA (Articles of Association)
4. File SPICe+ (Simplified Proforma for Incorporating Company Electronically Plus)
   along with eMOA and eAOA
5. Apply for PAN and TAN (included in SPICe+)
6. Obtain Certificate of Incorporation from ROC (Registrar of Companies)
7. Apply for GST registration (if applicable)
8. Open a bank account with the Certificate of Incorporation

### Timeline
- DSC procurement: 1-2 business days
- Name reservation (RUN): 2-3 business days (if no objection)
- SPICe+ filing and approval: 3-7 business days
- Total typical timeline: 7-15 business days


## 3. DIGITAL SIGNATURE CERTIFICATE (DSC)

### What is a DSC?
A Digital Signature Certificate is the electronic equivalent of a physical
signature. It is issued by Certifying Authorities (CAs) licensed by the
Controller of Certifying Authorities (CCA), Government of India. A Class 3
DSC is required for all MCA filings.

### Who Needs a DSC?
- All proposed directors of the company
- All subscribers to the MOA (if they are also filing)
- Designated partners of an LLP
- Any authorised signatory filing forms on MCA

### How to Obtain a DSC
1. Choose a licensed Certifying Authority (e.g., eMudhra, Sify, nCode, Capricorn)
2. Fill the DSC application form
3. Submit identity proof (PAN + Aadhaar for Indian nationals; Passport for
   foreign nationals)
4. Complete video verification (Aadhaar eKYC or in-person verification)
5. DSC is typically issued within 1-2 business days
6. The DSC is provided as a USB token or downloaded as a software certificate

### DSC Validity
- Typically valid for 2 years
- Must be renewed before expiry to continue filing
- Cost ranges from Rs 800 to Rs 2,000 depending on the CA and validity period


## 4. DIRECTOR IDENTIFICATION NUMBER (DIN)

### What is DIN?
A Director Identification Number is a unique 8-digit identification number
assigned to every individual who is a director (or intends to become a director)
of a company registered under the Companies Act, 2013.

### How to Get DIN
- For new companies: DIN is allotted as part of the SPICe+ form itself (no
  separate application needed)
- For existing directors joining a new company: Already have a DIN
- For appointment to an existing company: Apply using DIR-3 form
- DIN is a lifetime number -- it does not expire
- Each person can have only one DIN

### DIR-3 KYC
- Every DIN holder must file DIR-3 KYC annually before September 30
- Failure to file leads to DIN deactivation and a late fee of Rs 5,000
- Requires: PAN, Aadhaar, personal mobile number, personal email, address proof


## 5. MCA FILING PROCESS

### SPICe+ (INC-32)
SPICe+ is the integrated web form for company incorporation. It provides
multiple services in a single form:
- Part A: Name reservation (replaces standalone RUN form)
- Part B: Incorporation application including:
  - Company details (registered office address, objects, capital structure)
  - Director details (DIN allotment for up to 3 directors)
  - PAN & TAN application
  - EPFO & ESIC registration (optional)
  - GST registration (optional)
  - Professional Tax registration (for applicable states)
  - Bank account opening (mandatory DPIIT/Opening of Bank Account)

### RUN (Reserve Unique Name)
- Used to reserve a company name before or during incorporation
- Can propose up to 2 names per application
- Government fee: Rs 1,000 (resubmission: Rs 1,000 per attempt)
- Name is reserved for 20 days upon approval
- MCA checks for similarity with existing companies, trademarks, and
  undesirable names

### FiLLiP (Form for incorporation of LLP)
- The form used for incorporating an LLP
- Similar to SPICe+ but for LLP structure
- Includes LLP name reservation and DPIN allotment
- Requires filing of LLP Agreement within 30 days of incorporation

### AGILE-PRO-S
- Filed along with SPICe+ / FiLLiP
- Applies for GSTIN, EPFO, ESIC, Professional Tax, and bank account opening
- Mandatory for all new incorporations


## 6. POST-INCORPORATION REQUIREMENTS

### INC-20A (Declaration for Commencement of Business)
- Must be filed within 180 days of incorporation
- Declares that every subscriber has paid the value of shares agreed to be taken
- Filing fee: Rs 500
- Penalty for non-filing: Rs 50,000 for the company and Rs 1,000/day for
  every officer in default
- The company cannot commence business until this is filed

### First Board Meeting
- Must be held within 30 days of incorporation
- Key agenda items: appointment of first auditor, adoption of common seal (optional),
  registered office address confirmation, allotment of shares, opening bank account
- Minutes must be recorded and maintained

### Statutory Auditor Appointment
- The Board must appoint the first auditor within 30 days of incorporation
- The auditor holds office until the conclusion of the first AGM
- Form ADT-1 must be filed within 15 days of appointment

### Bank Account Opening
- Open a current account in the company's name using:
  - Certificate of Incorporation
  - MOA and AOA
  - PAN of the company
  - Board resolution authorizing account opening
  - KYC documents of all directors

### INC-22 (Registered Office Address)
- Must be filed within 30 days of incorporation if the registered office was
  not verified during SPICe+ filing
- Requires proof of registered office address


## 7. COMMON COMPLIANCE OBLIGATIONS

### Annual General Meeting (AGM) — Section 96
- **First AGM**: Must be held within 9 MONTHS from the close of the first
  financial year (NOT 6 months). This is a common misconception.
  Example: If incorporated in Oct 2025, first FY ends March 2026, first
  AGM must be held by December 31, 2026.
- **Subsequent AGMs**: Within 6 months from end of financial year
  (i.e., by September 30 for March year-end companies).
- **Maximum gap between two AGMs**: 15 months.
- **OPC**: Exempt from holding AGM (Section 96(1) proviso).
- **Penalty (Section 99)**: Up to Rs 1,00,000 on company + Rs 5,000/day
  for continuing default.

### Annual Filings (Every Year)
- **AOC-4**: Filing of financial statements with ROC within 30 days of AGM.
  For OPC: within 180 days of FY end (no AGM needed). Penalty: Rs 100/day,
  max Rs 10 lakh. (Section 137)
- **MGT-7/MGT-7A**: Filing of annual return within 60 days of AGM.
  Penalty: Rs 100/day, max Rs 10 lakh. (Section 92)
- **DIR-3 KYC**: Annual KYC for all DIN holders -- due by September 30.
  Late fee: Rs 5,000 and DIN gets deactivated. (Rule 12A)
- **ADT-1**: Auditor appointment/reappointment notice -- within 15 days of AGM.
  (Section 139)
- **Income Tax Return**: Filed by October 31 (if company requires audit under
  Section 44AB) or July 31 (otherwise). Late fee: Rs 5,000 (before Dec 31)
  or Rs 10,000 (after). (IT Act Section 139, 234F)

### Board Meetings — Section 173
- **Pvt Ltd / Public Ltd**: Minimum 4 board meetings per year with maximum
  120-day gap between consecutive meetings.
- **OPC / Section 8 / Small Company**: Minimum 2 board meetings per year,
  minimum 90-day gap between meetings.
- **First Board Meeting**: Within 30 days of incorporation.
- **Penalty**: Rs 25,000 on company + Rs 5,000 per director per default.

### GST Compliance
- **GSTR-1**: Monthly return for outward supplies -- due by 11th of next month.
  Quarterly option (QRMP scheme) available if turnover <= Rs 5 crore.
- **GSTR-3B**: Monthly summary return with tax payment -- due by 20th of next
  month (exact date varies by state category). Interest: 18% p.a. on late tax
  payment (Section 50 CGST Act).
- **GSTR-9**: Annual return -- due by December 31. Exempt if turnover <= Rs 2
  crore. Late fee: Rs 200/day (Rs 100 CGST + Rs 100 SGST), capped at 0.04%
  of turnover (NOT 0.25% -- that was the old cap). (CGST Act Section 44, 47)
- **GSTR-9C**: Self-certified reconciliation statement -- required if turnover
  exceeds Rs 5 crore. Due with GSTR-9 by December 31.
- GST registration is mandatory if turnover exceeds Rs 20 lakh (Rs 40 lakh
  for goods-only dealers in normal states; Rs 10 lakh for special category states).

### TDS Compliance
- Monthly TDS deduction and deposit by 7th of the following month
  (for March: by April 30)
- Quarterly TDS return filing: Q1 by Jul 31, Q2 by Oct 31, Q3 by Jan 31,
  Q4 by May 31 (Form 24Q for salary, 26Q for non-salary)
- Late fee: Rs 200/day under Section 234E (capped at TDS amount)
- Form 16 (salary) and Form 16A (non-salary) to be issued by June 15

### Other Important Filings
- **DPT-3**: Annual return of deposits and transactions NOT considered as
  deposits (inter-corporate loans, director loans). Due by June 30.
  Applicable to all Pvt Ltd and Public companies. (Section 73/74)
  Penalty: up to Rs 1 crore or 2x deposit amount. (Section 76A)
- **MSME Form I**: Half-yearly return if outstanding payments to MSME vendors
  exceed 45 days. Due: October 31 (H1: Apr-Sep) and April 30 (H2: Oct-Mar).
  (MSMED Act Section 22)
- **BEN-2**: Company must file within 30 days of receiving BEN-1 declaration
  from Significant Beneficial Owner (holding >= 10% shares/voting rights).
  Penalty: Rs 10 lakh + Rs 1,000/day. (Section 90)
- **MGT-14**: File copy of special resolutions and certain board resolutions
  with ROC within 30 days. (Section 117)
- **INC-20A**: Commencement of business declaration -- within 180 days of
  incorporation. Company CANNOT commence business until filed. Penalty:
  Rs 50,000 + Rs 1,000/day per officer. (Section 10A)

### LLP Specific Filings
- **Form 11**: LLP Annual Return -- within 60 days of FY end (by May 30).
  Penalty: Rs 100/day. (LLP Act Section 35, Rule 25)
- **Form 8**: Statement of Account & Solvency -- within 30 days from 6 months
  after FY end (by October 30). Penalty: Rs 100/day. (LLP Act Section 34, Rule 24)
- **DIR-3 KYC**: All DPIN holders by September 30. Late fee: Rs 5,000.


## 8. COSTS BREAKDOWN

### Government Fees
- Name reservation (RUN): Rs 1,000
- SPICe+ incorporation fee: Rs 500 (for authorized capital up to Rs 1 lakh)
  to Rs 2,000+ (for higher capital)
- Stamp duty: Varies by state (e.g., Delhi: 0.15% of authorized capital,
  Maharashtra: Rs 1,000 fixed, Karnataka: Rs 3,000 fixed approx.)
- DSC: Rs 800 - Rs 2,000 per director
- DIN allotment: Included in SPICe+ (no separate fee)
- PAN & TAN: Included in SPICe+

### Professional Fees
- Typical professional fees for Pvt Ltd incorporation: Rs 5,000 - Rs 15,000
  (varies by service provider, complexity, and state)
- Includes: document preparation, MOA/AOA drafting, form filing, government
  fee payment, post-incorporation assistance

### Total Estimated Costs (Pvt Ltd, 2 directors, Rs 1 lakh authorized capital)
- Government fees + stamp duty: Rs 3,000 - Rs 8,000 (varies by state)
- DSC for 2 directors: Rs 1,600 - Rs 4,000
- Professional fees: Rs 5,000 - Rs 15,000
- **Total: approximately Rs 10,000 - Rs 25,000**

### LLP Costs
- Generally lower than Pvt Ltd
- Government fee for FiLLiP: Rs 500
- LLP Agreement stamp duty: Varies by state
- Professional fees: Rs 4,000 - Rs 10,000
- **Total: approximately Rs 7,000 - Rs 18,000**

### OPC Costs
- Similar to Pvt Ltd costs
- Only 1 DSC needed (for the single director)
- **Total: approximately Rs 8,000 - Rs 20,000**


## 9. TIMELINE EXPECTATIONS

### Typical Timeline for Pvt Ltd Incorporation
| Step                                 | Duration             |
|--------------------------------------|----------------------|
| DSC procurement                      | 1-2 business days    |
| Name reservation (RUN/SPICe+ Part A) | 2-3 business days    |
| Document preparation (MOA, AOA)      | 1-2 business days    |
| SPICe+ filing and MCA processing     | 3-7 business days    |
| PAN & TAN issuance                   | Along with CIN       |
| Bank account opening                 | 2-5 business days    |
| GST registration                     | 3-7 business days    |

**Total: 7-15 business days** for incorporation (Certificate of Incorporation)
**Total with bank + GST: 15-25 business days** to be fully operational

### Factors That Can Delay Incorporation
- Incomplete or incorrect documents
- Name rejection by ROC (requires resubmission)
- MCA system downtime or technical issues
- ROC queries or additional information requests
- Incorrect DSC or DSC linkage issues
- High volume periods (e.g., end of financial year)
- State-specific stamp duty processing delays


## 10. COMMON MISTAKES FOUNDERS MAKE

1. **Choosing the wrong entity type**: Many founders register a Pvt Ltd when an
   LLP or OPC would be more appropriate, leading to unnecessary compliance burden.

2. **Not filing INC-20A on time**: This is one of the most commonly missed filings.
   The company legally cannot commence business without it, and penalties are steep.

3. **Ignoring DIR-3 KYC**: Directors forget the annual September 30 deadline,
   leading to DIN deactivation. Reactivation costs Rs 5,000 per director.

4. **Wrong registered office address**: Using a residential address without proper
   NOC or utility bills leads to rejection of incorporation application.

5. **Inadequate authorized capital**: Setting authorized capital too low (e.g.,
   Rs 1 lakh) and then needing to increase it later incurs additional stamp duty
   and ROC fees. Plan for at least 2-3 years of capital needs.

6. **Missing annual compliance deadlines**: Failure to file AOC-4 and MGT-7 leads
   to penalties of Rs 100/day (up to Rs 10 lakh) and potential strike-off of the
   company.

7. **Not maintaining statutory registers**: Companies Act requires maintenance of
   registers of members, directors, charges, etc. These are often ignored.

8. **Mixing personal and company finances**: Using personal bank accounts for
   company transactions creates tax and legal complications.

9. **Not having a shareholders' agreement**: While not legally mandatory, a
   shareholders' agreement prevents future disputes about equity, exits, and
   decision-making authority.

10. **Delaying GST registration**: If your turnover is approaching the threshold
    or you are doing interstate sales, register for GST early. Late registration
    means you cannot claim input tax credit for the period you were unregistered.

11. **Not appointing an auditor within 30 days**: The Board must appoint the first
    auditor within 30 days. Failure attracts penalties and complications.

12. **Skipping the first board meeting**: The first board meeting within 30 days of
    incorporation is mandatory. Missing it is a compliance violation.
"""

# Topic tags for keyword-based search fallback
KNOWLEDGE_TOPICS = {
    "company_types": {
        "keywords": [
            "type", "types", "entity", "pvt", "private", "limited", "opc",
            "one person", "llp", "partnership", "section 8", "non-profit",
            "ngo", "sole", "proprietorship", "which", "choose", "best",
            "structure", "right entity", "startup", "formation",
        ],
        "section": "1. TYPES OF COMPANIES IN INDIA",
        "source": "Company Types in India",
    },
    "incorporation_process": {
        "keywords": [
            "incorporate", "incorporation", "process", "steps", "how to",
            "register", "registration", "start", "form", "documents",
            "document", "needed", "required", "timeline", "procedure",
        ],
        "section": "2. INCORPORATION PROCESS OVERVIEW",
        "source": "Incorporation Process",
    },
    "dsc": {
        "keywords": [
            "dsc", "digital signature", "signature certificate", "sign",
            "usb token", "certifying authority", "emudhra",
        ],
        "section": "3. DIGITAL SIGNATURE CERTIFICATE (DSC)",
        "source": "Digital Signature Certificate (DSC)",
    },
    "din": {
        "keywords": [
            "din", "director identification", "dir-3", "dir3", "kyc",
            "director number",
        ],
        "section": "4. DIRECTOR IDENTIFICATION NUMBER (DIN)",
        "source": "Director Identification Number (DIN)",
    },
    "mca_filing": {
        "keywords": [
            "mca", "spice", "spice+", "spicee", "fillip", "run", "name",
            "reservation", "agile", "filing", "roc", "registrar",
        ],
        "section": "5. MCA FILING PROCESS",
        "source": "MCA Filing Process",
    },
    "post_incorporation": {
        "keywords": [
            "after", "post", "inc-20a", "inc20a", "commencement", "first",
            "board meeting", "auditor", "bank account", "inc-22", "inc22",
            "pan", "tan",
        ],
        "section": "6. POST-INCORPORATION REQUIREMENTS",
        "source": "Post-Incorporation Requirements",
    },
    "compliance": {
        "keywords": [
            "compliance", "annual", "filing", "aoc-4", "aoc4", "mgt-7",
            "mgt7", "gst", "gstr", "tds", "tax", "return", "agm",
            "income tax", "msme", "dpt-3", "dpt3",
        ],
        "section": "7. COMMON COMPLIANCE OBLIGATIONS",
        "source": "Compliance Obligations",
    },
    "costs": {
        "keywords": [
            "cost", "costs", "fee", "fees", "price", "pricing", "how much",
            "expensive", "cheap", "stamp duty", "government fee",
            "professional fee", "budget", "money", "pay", "payment",
            "charges", "amount",
        ],
        "section": "8. COSTS BREAKDOWN",
        "source": "Costs Breakdown",
    },
    "timeline": {
        "keywords": [
            "time", "timeline", "how long", "duration", "days", "weeks",
            "fast", "quick", "delay", "speed", "when", "take",
        ],
        "section": "9. TIMELINE EXPECTATIONS",
        "source": "Timeline Expectations",
    },
    "mistakes": {
        "keywords": [
            "mistake", "mistakes", "error", "avoid", "wrong", "common",
            "problem", "issue", "tip", "tips", "advice", "pitfall",
            "careful", "warning",
        ],
        "section": "10. COMMON MISTAKES FOUNDERS MAKE",
        "source": "Common Mistakes",
    },
}


def extract_section(section_heading: str) -> str:
    """Extract a specific section from the knowledge base by heading."""
    lines = KNOWLEDGE_BASE.split("\n")
    capturing = False
    result = []
    for line in lines:
        if section_heading in line:
            capturing = True
            result.append(line)
            continue
        if capturing:
            # Stop at the next top-level section heading (## N.)
            if line.startswith("## ") and line[3:4].isdigit() and section_heading not in line:
                break
            result.append(line)
    return "\n".join(result).strip()


def keyword_search(query: str, max_sections: int = 3) -> "tuple[str, list[str]]":
    """
    Search the knowledge base using keyword matching.

    Returns a tuple of (relevant_text, list_of_source_names).
    """
    query_lower = query.lower()
    query_words = set(query_lower.split())

    scored_topics = []  # list of (topic_id, score, title, section_text)

    for topic_id, topic_info in KNOWLEDGE_TOPICS.items():
        score = 0
        for keyword in topic_info["keywords"]:
            # Exact phrase match in query
            if keyword in query_lower:
                score += 3 if len(keyword) > 3 else 1
            # Individual word match
            keyword_words = set(keyword.split())
            overlap = query_words & keyword_words
            score += len(overlap)

        if score > 0:
            scored_topics.append(
                (topic_id, score, topic_info["section"], topic_info["source"])
            )

    # Sort by score descending
    scored_topics.sort(key=lambda x: x[1], reverse=True)

    if not scored_topics:
        # Default: return the company types and incorporation overview
        sections = [
            extract_section("1. TYPES OF COMPANIES IN INDIA"),
            extract_section("2. INCORPORATION PROCESS OVERVIEW"),
        ]
        return "\n\n".join(sections), [
            "Company Types in India",
            "Incorporation Process",
        ]

    # Take top N sections
    top_topics = scored_topics[:max_sections]
    sections = [extract_section(t[2]) for t in top_topics]
    sources = [t[3] for t in top_topics]

    return "\n\n".join(sections), sources
