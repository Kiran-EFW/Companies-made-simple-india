"""Shared HTML utilities for legal document rendering.

Provides the base HTML wrapper with Indian legal compliance features:
- Page numbering (Page X of Y)
- DRAFT watermark for non-finalized documents
- Stamp duty notice (Indian Stamp Act 1899) with state-wise rates for all entity types
- E-signature vs DSC distinction notice
- DD/MM/YYYY date format (Indian standard)
- A4 page layout with proper margins
"""

from datetime import datetime
from typing import Optional


def format_date_indian(date_str: str) -> str:
    """Convert date string to Indian DD/MM/YYYY format."""
    if not date_str:
        return ""
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            parsed = datetime.strptime(date_str, fmt)
            return parsed.strftime("%d/%m/%Y")
        except ValueError:
            continue
    return date_str


# ---------------------------------------------------------------------------
# Complete State & UT-Wise Stamp Duty Rates (India 2024/2025)
# For All Entity Types: Pvt Ltd, OPC, Section 8, LLP, Partnership, Sole Prop
#
# Source: Respective State Stamp Acts, MCA SPICe+ portal, state IGR websites
# WARNING: Rates are subject to frequent amendments. Always verify via MCA
# portal SPICe+ tools or state IGR websites before final filing.
# Surcharges or cess may apply based on capital and entity structure.
# ---------------------------------------------------------------------------

STAMP_DUTY_RATES: dict = {
    # ---- 28 States ----
    "Andhra Pradesh": {
        "moa": "\u20b9500", "aoa": "\u20b91,500", "llp": "\u20b9500 (base)",
        "partnership": "Variable, tied to capital contribution",
        "sole_prop_affidavit": "State affidavit rate",
        "section_8_exempt": False, "section_8_note": "Nominal \u20b9500",
    },
    "Arunachal Pradesh": {
        "moa": "\u20b9100", "aoa": "\u20b9300", "llp": "\u20b9100",
        "partnership": "Nominal", "sole_prop_affidavit": "State affidavit rate",
        "section_8_exempt": False,
    },
    "Assam": {
        "moa": "\u20b9100", "aoa": "\u20b9300", "llp": "\u20b9100",
        "partnership": "Nominal", "sole_prop_affidavit": "State affidavit rate",
        "section_8_exempt": False, "section_8_note": "Nominal \u20b9200",
    },
    "Bihar": {
        "moa": "\u20b9500", "aoa": "\u20b91,500",
        "llp": "2.5% of capital (max \u20b95,000)",
        "partnership": "Tied to capital contribution",
        "sole_prop_affidavit": "State affidavit rate",
        "section_8_exempt": True,
    },
    "Chhattisgarh": {
        "moa": "\u20b9500", "aoa": "\u20b91,500",
        "llp": "Slab-based (\u20b92,000\u2013\u20b95,000)",
        "partnership": "Variable", "sole_prop_affidavit": "State affidavit rate",
        "section_8_exempt": False,
    },
    "Goa": {
        "moa": "\u20b9150", "aoa": "\u20b9150", "llp": "\u20b9150",
        "partnership": "Nominal", "sole_prop_affidavit": "State affidavit rate",
        "section_8_exempt": False,
    },
    "Gujarat": {
        "moa": "\u20b9100", "aoa": "Varies (max \u20b915L)",
        "llp": "Slab: \u20b91,000 (\u22641L) to \u20b910,000 (>10L)",
        "partnership": "Slab-based on capital",
        "sole_prop_affidavit": "State affidavit rate",
        "section_8_exempt": False,
    },
    "Haryana": {
        "moa": "\u20b960", "aoa": "\u20b960\u2013\u20b9120",
        "llp": "\u20b91,000 (flat)",
        "partnership": "Tied to capital",
        "sole_prop_affidavit": "State affidavit rate",
        "section_8_exempt": True,
    },
    "Himachal Pradesh": {
        "moa": "\u20b9100", "aoa": "\u20b9300", "llp": "\u20b9100",
        "partnership": "Nominal", "sole_prop_affidavit": "State affidavit rate",
        "section_8_exempt": False,
    },
    "Jharkhand": {
        "moa": "\u20b963", "aoa": "\u20b9105",
        "llp": "2.5% of capital (max \u20b95,000)",
        "partnership": "Tied to capital contribution",
        "sole_prop_affidavit": "State affidavit rate",
        "section_8_exempt": True,
    },
    "Karnataka": {
        "moa": "\u20b95,000",
        "aoa": "\u20b95,000 + \u20b91,000/\u20b95L >\u20b910L (max \u20b925L)",
        "llp": "\u20b91,000 + \u20b9500/\u20b95L >\u20b910L (max \u20b910L)",
        "partnership": "\u20b9500 flat (capital >\u20b9500)",
        "sole_prop_affidavit": "\u20b9100",
        "section_8_exempt": False,
    },
    "Kerala": {
        "moa": "\u20b91,000", "aoa": "\u20b92,000", "llp": "\u20b95,000 (flat)",
        "partnership": "Variable", "sole_prop_affidavit": "State affidavit rate",
        "section_8_exempt": False,
    },
    "Madhya Pradesh": {
        "moa": "\u20b92,500", "aoa": "\u20b95,000",
        "llp": "Slab-based (\u20b92,000\u2013\u20b95,000)",
        "partnership": "Variable", "sole_prop_affidavit": "State affidavit rate",
        "section_8_exempt": False,
    },
    "Maharashtra": {
        "moa": "\u20b9200", "aoa": "0.3% of share capital (max \u20b91 Cr)",
        "llp": "1% of capital (max \u20b950,000)",
        "partnership": "\u20b9500 (<\u20b950K), 1% (>\u20b950K, max \u20b915,000)",
        "sole_prop_affidavit": "\u20b9500",
        "section_8_exempt": True,
    },
    "Manipur": {
        "moa": "\u20b9100", "aoa": "\u20b9150", "llp": "\u20b9100",
        "partnership": "Nominal", "sole_prop_affidavit": "State affidavit rate",
        "section_8_exempt": False,
    },
    "Meghalaya": {
        "moa": "\u20b9100", "aoa": "\u20b9300", "llp": "\u20b9100",
        "partnership": "Nominal", "sole_prop_affidavit": "State affidavit rate",
        "section_8_exempt": False,
    },
    "Mizoram": {
        "moa": "\u20b9100", "aoa": "\u20b9150", "llp": "\u20b9100",
        "partnership": "Nominal", "sole_prop_affidavit": "State affidavit rate",
        "section_8_exempt": False,
    },
    "Nagaland": {
        "moa": "\u20b9100", "aoa": "\u20b9150", "llp": "\u20b9100",
        "partnership": "Nominal", "sole_prop_affidavit": "State affidavit rate",
        "section_8_exempt": False,
    },
    "Odisha": {
        "moa": "\u20b9300", "aoa": "\u20b9300", "llp": "\u20b9200",
        "partnership": "Variable", "sole_prop_affidavit": "State affidavit rate",
        "section_8_exempt": False,
    },
    "Punjab": {
        "moa": "\u20b95,000", "aoa": "\u20b95,000", "llp": "\u20b91,000",
        "partnership": "Variable", "sole_prop_affidavit": "State affidavit rate",
        "section_8_exempt": False,
    },
    "Rajasthan": {
        "moa": "\u20b9500", "aoa": "\u20b97,500",
        "llp": "\u20b92,000 per \u20b950,000 increment",
        "partnership": "Variable", "sole_prop_affidavit": "State affidavit rate",
        "section_8_exempt": False,
    },
    "Sikkim": {
        "moa": "\u20b90", "aoa": "\u20b90", "llp": "\u20b9100",
        "partnership": "Nominal/NIL", "sole_prop_affidavit": "Nominal",
        "section_8_exempt": True,
    },
    "Tamil Nadu": {
        "moa": "\u20b9200", "aoa": "0.05% of capital (max \u20b95L)",
        "llp": "\u20b9300 (flat, capital >\u20b9500)",
        "partnership": "1% of capital (max \u20b925,000)",
        "sole_prop_affidavit": "State affidavit rate",
        "section_8_exempt": True,
    },
    "Telangana": {
        "moa": "\u20b9500", "aoa": "\u20b91,500", "llp": "\u20b9300 (base)",
        "partnership": "Variable", "sole_prop_affidavit": "State affidavit rate",
        "section_8_exempt": False,
    },
    "Tripura": {
        "moa": "\u20b9100", "aoa": "\u20b9150", "llp": "\u20b9100",
        "partnership": "Nominal", "sole_prop_affidavit": "State affidavit rate",
        "section_8_exempt": False,
    },
    "Uttar Pradesh": {
        "moa": "\u20b9500", "aoa": "\u20b9500",
        "llp": "0.15% of capital (max \u20b910,000)",
        "partnership": "Variable", "sole_prop_affidavit": "State affidavit rate",
        "section_8_exempt": False,
    },
    "Uttarakhand": {
        "moa": "\u20b9500", "aoa": "\u20b91,500", "llp": "\u20b9750",
        "partnership": "Variable", "sole_prop_affidavit": "State affidavit rate",
        "section_8_exempt": False,
    },
    "West Bengal": {
        "moa": "\u20b960", "aoa": "\u20b9300", "llp": "\u20b9150",
        "partnership": "Variable",
        "sole_prop_affidavit": "From \u20b920",
        "section_8_exempt": False,
    },
    # ---- 8 Union Territories ----
    "Andaman & Nicobar": {
        "moa": "\u20b9200", "aoa": "\u20b9300",
        "llp": "\u20b9100\u2013\u20b9200",
        "partnership": "Nominal", "sole_prop_affidavit": "Nominal",
        "section_8_exempt": True,
    },
    "Chandigarh": {
        "moa": "\u20b9500", "aoa": "\u20b9500 (slab-based)",
        "llp": "\u20b9500\u2013\u20b91,000",
        "partnership": "Variable", "sole_prop_affidavit": "State affidavit rate",
        "section_8_exempt": False,
    },
    "Dadra & Nagar Haveli and Daman & Diu": {
        "moa": "\u20b9150", "aoa": "\u20b91,000/\u20b95L capital",
        "llp": "\u20b9150\u2013\u20b9500",
        "partnership": "Nominal", "sole_prop_affidavit": "Nominal",
        "section_8_exempt": False,
    },
    "Delhi": {
        "moa": "\u20b9200", "aoa": "0.15% of capital (max \u20b925L)",
        "llp": "1% of capital (max \u20b95,000)",
        "partnership": "1% of capital (max \u20b95,000)",
        "sole_prop_affidavit": "State affidavit rate",
        "section_8_exempt": True,
    },
    "Jammu & Kashmir": {
        "moa": "\u20b9150", "aoa": "\u20b9150",
        "llp": "\u20b9100\u2013\u20b9150",
        "partnership": "Nominal", "sole_prop_affidavit": "Nominal",
        "section_8_exempt": True,
    },
    "Ladakh": {
        "moa": "\u20b90", "aoa": "\u20b90", "llp": "\u20b9100",
        "partnership": "Nominal/NIL", "sole_prop_affidavit": "Nominal",
        "section_8_exempt": True,
    },
    "Lakshadweep": {
        "moa": "\u20b9500", "aoa": "\u20b91,000",
        "llp": "\u20b9150\u2013\u20b9500",
        "partnership": "Nominal", "sole_prop_affidavit": "Nominal",
        "section_8_exempt": False,
    },
    "Puducherry": {
        "moa": "\u20b9200", "aoa": "\u20b9300",
        "llp": "\u20b9100\u2013\u20b9200",
        "partnership": "Nominal", "sole_prop_affidavit": "Nominal",
        "section_8_exempt": True,
    },
}

# States/UTs with confirmed Section 8 NIL stamp duty
SECTION_8_EXEMPT_JURISDICTIONS: list[str] = [
    s for s, r in STAMP_DUTY_RATES.items() if r.get("section_8_exempt")
]

# Entity type labels for stamp duty notices
ENTITY_TYPE_LABELS = {
    "private_limited": "Private Limited Company",
    "opc": "One Person Company (OPC)",
    "section_8": "Section 8 (Not-for-Profit) Company",
    "llp": "Limited Liability Partnership",
    "partnership": "General Partnership",
    "sole_proprietorship": "Sole Proprietorship",
}


def get_stamp_duty_html(
    state: Optional[str] = None,
    entity_type: Optional[str] = None,
) -> str:
    """Generate stamp duty notice HTML with state and entity-type awareness.

    Args:
        state: Indian state/UT name to show specific rates.
        entity_type: One of 'private_limited', 'opc', 'section_8', 'llp',
                     'partnership', 'sole_proprietorship'.
    """
    rates = STAMP_DUTY_RATES.get(state) if state else None

    # --- Entity-specific header notes ---
    entity_note = ""
    if entity_type == "section_8":
        if rates and rates.get("section_8_exempt"):
            entity_note = (
                f'<strong>Section 8 Company \u2014 {state}:</strong> '
                f'Stamp duty on MOA and AOA is <strong>NIL</strong> '
                f'(100% exemption for not-for-profit entities).<br>'
            )
        elif rates and rates.get("section_8_note"):
            entity_note = (
                f'<strong>Section 8 Company \u2014 {state}:</strong> '
                f'{rates["section_8_note"]}.<br>'
            )
        else:
            entity_note = (
                '<strong>Section 8 (Not-for-Profit):</strong> Most major jurisdictions '
                'provide NIL stamp duty, including: Delhi, Haryana, Maharashtra, '
                'Tamil Nadu, Bihar, Jharkhand, J&amp;K, and Puducherry.<br>'
            )
    elif entity_type == "opc":
        entity_note = (
            '<strong>OPC Note:</strong> One Person Companies follow the same stamp '
            'duty as Private Limited Companies. OPCs cannot exceed \u20b950L authorized '
            'capital, so they typically hit the lowest AOA slab rate.<br>'
        )
    elif entity_type == "sole_proprietorship":
        if rates and rates.get("sole_prop_affidavit"):
            entity_note = (
                f'<strong>Sole Proprietorship \u2014 {state}:</strong> '
                f'Affidavit stamp duty: {rates["sole_prop_affidavit"]}. '
                f'No MCA filing required; registration is via GST, MSME Udyam, '
                f'and Shop & Establishment licences.<br>'
            )
        else:
            entity_note = (
                '<strong>Sole Proprietorship:</strong> Not registered with MCA. '
                'Banks may require a sworn Affidavit of Sole Proprietorship on '
                'stamp paper (flat rate per state Stamp Act for affidavits).<br>'
            )
    elif entity_type == "partnership":
        if rates and rates.get("partnership"):
            entity_note = (
                f'<strong>Partnership Deed \u2014 {state}:</strong> '
                f'{rates["partnership"]}. Partnership Deeds are executed on '
                f'physical non-judicial stamp paper with the state registrar, '
                f'not via MCA.<br>'
            )
        else:
            entity_note = (
                '<strong>Partnership Deed:</strong> Rates are highly variable and '
                'tied to capital contribution. Executed on physical stamp paper '
                'with the state registrar, not MCA.<br>'
            )

    # --- State-specific or generic rate block ---
    if rates and entity_type not in ("sole_proprietorship",):
        rate_lines = (
            f'<strong>Stamp duty for {state}:</strong><br>'
            f'MOA: {rates["moa"]} &nbsp;|&nbsp; '
            f'AOA: {rates["aoa"]} &nbsp;|&nbsp; '
            f'LLP Agreement: {rates["llp"]}'
        )
        if rates.get("partnership") and entity_type in ("partnership", None):
            rate_lines += f' &nbsp;|&nbsp; Partnership: {rates["partnership"]}'
        rate_lines += '<br>'
        state_block = rate_lines
    elif entity_type == "sole_proprietorship":
        state_block = ""  # No MOA/AOA rates apply
    else:
        state_block = (
            '<strong>Indicative Stamp Duty Rates (2024/2025):</strong><br>'
            '<em>Maharashtra:</em> MOA &#8377;200; AOA 0.3% of capital (max &#8377;1 Cr); '
            'LLP 1% (max &#8377;50,000); Partnership &#8377;500/1% (max &#8377;15,000).<br>'
            '<em>Karnataka:</em> MOA &#8377;5,000; AOA &#8377;5,000 + &#8377;1,000/&#8377;5L '
            '&gt;&#8377;10L (max &#8377;25L); Partnership &#8377;500 flat.<br>'
            '<em>Delhi:</em> MOA &#8377;200; AOA 0.15% (max &#8377;25L); '
            'LLP/Partnership 1% (max &#8377;5,000).<br>'
            '<em>Tamil Nadu:</em> MOA &#8377;200; AOA 0.05% (max &#8377;5L); '
            'Partnership 1% (max &#8377;25,000).<br>'
            '<em>Gujarat:</em> MOA &#8377;100; AOA varies (max &#8377;15L); '
            'LLP &#8377;1,000&ndash;&#8377;10,000.<br>'
        )

    # --- Payment mechanism note ---
    payment_note = (
        '<em>Companies (Pvt Ltd, OPC, Sec 8): stamp duty is paid online via MCA '
        'SPICe+ portal. LLPs (Form 3) &amp; Partnerships: must be on state-specific '
        'non-judicial stamp paper (e-stamping via SHCIL where available), notarized, '
        'then filed.</em><br>'
    )

    return (
        '<div style="margin-top:12px;padding:10px 12px;background:#fffbeb;'
        'border:1px solid #fde68a;font-size:8pt;color:#92400e;">'
        '<strong>Stamp Duty Notice:</strong> This document may require stamping under the '
        'Indian Stamp Act, 1899 (as amended by the Indian Stamp (Amendment) Act, 2023) or '
        'applicable state stamp legislation. An unstamped or insufficiently stamped document '
        'is inadmissible as evidence in court proceedings (Section 35, Indian Stamp Act).'
        '<br><br>'
        f'{entity_note}'
        f'{state_block}'
        '<br>'
        f'{payment_note}'
        '<em>Rates are indicative and subject to change. Verify via MCA portal or state '
        'IGR website before filing. Surcharges or cess may apply.</em>'
        '</div>'
    )


_ESIGN_NOTICE = (
    '<div style="margin-top:8px;padding:10px 12px;background:#f0f9ff;'
    'border:1px solid #bae6fd;font-size:8pt;color:#0c4a6e;">'
    '<strong>Electronic Signatures:</strong> If this document is signed electronically, '
    'electronic signatures are legally valid under the Information Technology Act, 2000 '
    '(Section 3A). Note: For filings with MCA (Ministry of Corporate Affairs), only '
    'Digital Signature Certificates (DSC) issued by Certifying Authorities licensed under '
    'the IT Act are accepted. Aadhaar-based e-Sign is <strong>not</strong> accepted for '
    'MCA filings.<br>'
    '<strong>MCA forms requiring DSC:</strong> SPICe+ (INC-32), e-MOA, e-AOA, Form 3 '
    '(LLP Agreement), DIR-12, INC-22, AOC-4, MGT-7.<br>'
    '<em>As per CCA guidelines effective 1 July 2024, stricter eKYC, telephonic, '
    'and video verification is mandatory for new DSC issuance.</em><br>'
    'E-signatures on this platform are valid for private agreements between parties '
    'but are not a substitute for DSC-based signing required for regulatory filings.'
    '</div>'
)

_DISCLAIMER = (
    '<div style="margin-top:32px;padding:12px;background:#f9f9f9;'
    'border:1px solid #ddd;font-size:9pt;color:#666;">'
    '<strong>Disclaimer:</strong> This document is generated as a template and does not '
    'constitute legal advice. Please have this document reviewed by a qualified legal '
    'professional before execution.'
    '</div>'
)


def get_legal_notices(
    state: Optional[str] = None,
    entity_type: Optional[str] = None,
) -> str:
    """Build the full legal notices block with optional state/entity awareness."""
    return (
        _DISCLAIMER
        + get_stamp_duty_html(state, entity_type)
        + _ESIGN_NOTICE
    )


# Default notices (no state/entity context) for backward compatibility
_LEGAL_NOTICES = get_legal_notices()


# ---------------------------------------------------------------------------
# Company Letterhead System — Section 12(3)(c) Compliance
#
# Companies Act 2013, Section 12(3)(c): Every company shall have its name,
# address of its registered office, CIN, telephone number, fax number (if any),
# email and website addresses (if any) printed on all business letters,
# bill-heads, letter papers, notices and other official publications.
# Penalty: Rs 1,000 per day, max Rs 1,00,000 (Section 12(8)).
# ---------------------------------------------------------------------------

# Available letterhead designs
LETTERHEAD_DESIGNS = {
    "classic": "Classic — centered header with serif typography, traditional Indian corporate style",
    "modern": "Modern — clean left-aligned layout with accent color bar, contemporary look",
    "formal": "Formal — structured box-framed header with tabular detail layout",
    "minimal": "Minimal — lightweight text header with subtle separator, suits tech companies",
    "executive": "Executive — premium dual-tone header with logo placement, suited for board documents",
}

# Default accent colors per design
_DEFAULT_COLORS = {
    "classic": "#1a365d",    # Navy
    "modern": "#0d6efd",     # Blue
    "formal": "#2c3e50",     # Dark slate
    "minimal": "#374151",    # Gray-700
    "executive": "#0f172a",  # Slate-900
}


def generate_letterhead(
    *,
    company_name: str,
    cin: str = "",
    registered_office: str = "",
    phone: str = "",
    email: str = "",
    website: str = "",
    pan: str = "",
    tan: str = "",
    design: str = "classic",
    accent_color: str = "",
    logo_html: str = "",
    tagline: str = "",
    show_pan_tan: bool = False,
) -> dict:
    """Generate letterhead header and footer HTML.

    Returns dict with keys:
        header: HTML for document header / letterhead
        footer: HTML for document footer
        design: Design name used

    All designs include Section 12(3)(c) mandatory elements.
    """
    color = accent_color or _DEFAULT_COLORS.get(design, "#1a365d")

    # Build the contact line (used by all designs)
    contact_parts: list[str] = []
    if phone:
        contact_parts.append(f"Tel: {phone}")
    if email:
        contact_parts.append(f"Email: {email}")
    if website:
        contact_parts.append(website)
    contact_line = " &nbsp;|&nbsp; ".join(contact_parts) if contact_parts else ""

    # PAN/TAN line
    id_parts: list[str] = []
    if show_pan_tan:
        if pan:
            id_parts.append(f"PAN: {pan}")
        if tan:
            id_parts.append(f"TAN: {tan}")
    id_line = " &nbsp;|&nbsp; ".join(id_parts) if id_parts else ""

    generators = {
        "classic": _letterhead_classic,
        "modern": _letterhead_modern,
        "formal": _letterhead_formal,
        "minimal": _letterhead_minimal,
        "executive": _letterhead_executive,
    }
    gen = generators.get(design, _letterhead_classic)
    header = gen(
        company_name=company_name, cin=cin, registered_office=registered_office,
        contact_line=contact_line, id_line=id_line, color=color,
        logo_html=logo_html, tagline=tagline,
    )
    footer = _letterhead_footer(company_name=company_name, cin=cin, color=color, design=design)
    return {"header": header, "footer": footer, "design": design}


def _letterhead_classic(
    *, company_name: str, cin: str, registered_office: str,
    contact_line: str, id_line: str, color: str,
    logo_html: str, tagline: str,
) -> str:
    """Classic — centered, serif, traditional Indian corporate."""
    return (
        f'<div style="text-align:center; border-bottom:3px double {color}; '
        f'padding-bottom:15px; margin-bottom:25px;">'
        + (f'<div style="margin-bottom:8px;">{logo_html}</div>' if logo_html else '')
        + f'<h1 style="margin:0; font-size:22px; font-family:Georgia,serif; '
        f'color:{color}; text-transform:uppercase; letter-spacing:2px;">'
        f'{company_name}</h1>'
        + (f'<p style="margin:3px 0; font-size:11px; font-style:italic; '
           f'color:#666;">{tagline}</p>' if tagline else '')
        + (f'<p style="margin:4px 0; font-size:10px; color:#555;">CIN: {cin}</p>'
           if cin else '')
        + (f'<p style="margin:3px 0; font-size:10px; color:#555;">'
           f'Registered Office: {registered_office}</p>'
           if registered_office else '')
        + (f'<p style="margin:3px 0; font-size:9px; color:#777;">'
           f'{contact_line}</p>'
           if contact_line else '')
        + (f'<p style="margin:2px 0; font-size:9px; color:#888;">'
           f'{id_line}</p>'
           if id_line else '')
        + '</div>'
    )


def _letterhead_modern(
    *, company_name: str, cin: str, registered_office: str,
    contact_line: str, id_line: str, color: str,
    logo_html: str, tagline: str,
) -> str:
    """Modern — left-aligned with accent bar, contemporary."""
    return (
        f'<div style="border-left:5px solid {color}; padding-left:18px; '
        f'margin-bottom:25px; padding-bottom:12px; '
        f'border-bottom:1px solid #e5e7eb;">'
        + (f'<div style="margin-bottom:6px;">{logo_html}</div>' if logo_html else '')
        + f'<h1 style="margin:0; font-size:20px; font-family:\'Helvetica Neue\','
        f'Arial,sans-serif; color:{color}; letter-spacing:1px;">'
        f'{company_name}</h1>'
        + (f'<p style="margin:2px 0; font-size:11px; color:#6b7280;">'
           f'{tagline}</p>' if tagline else '')
        + f'<div style="display:flex; flex-wrap:wrap; gap:12px; margin-top:6px; '
        f'font-size:9px; color:#6b7280;">'
        + (f'<span>CIN: {cin}</span>' if cin else '')
        + (f'<span>{contact_line}</span>' if contact_line else '')
        + '</div>'
        + (f'<p style="margin:2px 0; font-size:9px; color:#9ca3af;">'
           f'Regd. Office: {registered_office}</p>'
           if registered_office else '')
        + (f'<p style="margin:1px 0; font-size:8px; color:#9ca3af;">'
           f'{id_line}</p>'
           if id_line else '')
        + '</div>'
    )


def _letterhead_formal(
    *, company_name: str, cin: str, registered_office: str,
    contact_line: str, id_line: str, color: str,
    logo_html: str, tagline: str,
) -> str:
    """Formal — box-framed with tabular layout, government/institutional."""
    return (
        f'<div style="border:2px solid {color}; padding:15px; margin-bottom:25px;">'
        '<div style="display:flex; align-items:center; gap:15px;">'
        + (f'<div style="flex-shrink:0;">{logo_html}</div>' if logo_html else '')
        + '<div style="flex:1;">'
        + f'<h1 style="margin:0; font-size:20px; font-family:Georgia,serif; '
        f'color:{color}; text-transform:uppercase; text-align:center; '
        f'letter-spacing:1.5px;">{company_name}</h1>'
        + (f'<p style="text-align:center; margin:2px 0; font-size:10px; '
           f'font-style:italic; color:#666;">{tagline}</p>'
           if tagline else '')
        + '</div></div>'
        + f'<table style="width:100%; border-collapse:collapse; margin-top:10px; '
        f'font-size:9px; color:#555; border:none;">'
        + (f'<tr><td style="padding:2px 8px; border:none; width:50%;">'
           f'<strong>CIN:</strong> {cin}</td>'
           f'<td style="padding:2px 8px; border:none;">'
           f'<strong>Regd. Office:</strong> {registered_office}</td></tr>'
           if cin or registered_office else '')
        + (f'<tr><td colspan="2" style="padding:2px 8px; border:none;">'
           f'{contact_line}</td></tr>'
           if contact_line else '')
        + (f'<tr><td colspan="2" style="padding:2px 8px; border:none; '
           f'font-size:8px; color:#888;">{id_line}</td></tr>'
           if id_line else '')
        + '</table>'
        + '</div>'
    )


def _letterhead_minimal(
    *, company_name: str, cin: str, registered_office: str,
    contact_line: str, id_line: str, color: str,
    logo_html: str, tagline: str,
) -> str:
    """Minimal — lightweight, suits tech/startup companies."""
    return (
        '<div style="margin-bottom:25px; padding-bottom:10px; '
        'border-bottom:1px solid #e5e7eb;">'
        '<div style="display:flex; align-items:baseline; gap:12px;">'
        + (f'<div>{logo_html}</div>' if logo_html else '')
        + f'<h1 style="margin:0; font-size:18px; font-family:\'Helvetica Neue\','
        f'Arial,sans-serif; color:{color}; font-weight:600;">'
        f'{company_name}</h1>'
        + (f'<span style="font-size:10px; color:#9ca3af;">|&nbsp;{tagline}</span>'
           if tagline else '')
        + '</div>'
        + f'<p style="margin:4px 0 0 0; font-size:8px; color:#9ca3af;">'
        + ' &nbsp;&middot;&nbsp; '.join(
            [x for x in [
                f'CIN: {cin}' if cin else '',
                registered_office if registered_office else '',
                contact_line.replace(' &nbsp;|&nbsp; ', ' &middot; ') if contact_line else '',
                id_line.replace(' &nbsp;|&nbsp; ', ' &middot; ') if id_line else '',
            ] if x]
        )
        + '</p></div>'
    )


def _letterhead_executive(
    *, company_name: str, cin: str, registered_office: str,
    contact_line: str, id_line: str, color: str,
    logo_html: str, tagline: str,
) -> str:
    """Executive — premium dual-tone, suited for board documents."""
    return (
        f'<div style="margin-bottom:25px;">'
        f'<div style="background:{color}; color:white; padding:14px 20px; '
        f'display:flex; align-items:center; gap:15px;">'
        + (f'<div style="flex-shrink:0;">{logo_html}</div>' if logo_html else '')
        + f'<div style="flex:1;">'
        f'<h1 style="margin:0; font-size:20px; font-family:Georgia,serif; '
        f'color:white; text-transform:uppercase; letter-spacing:2px;">'
        f'{company_name}</h1>'
        + (f'<p style="margin:2px 0 0 0; font-size:10px; color:rgba(255,255,255,0.8); '
           f'font-style:italic;">{tagline}</p>' if tagline else '')
        + '</div></div>'
        + f'<div style="background:#f8f9fa; padding:8px 20px; '
        f'border-bottom:2px solid {color}; font-size:9px; color:#555; '
        f'display:flex; flex-wrap:wrap; gap:15px;">'
        + (f'<span><strong>CIN:</strong> {cin}</span>' if cin else '')
        + (f'<span><strong>Regd. Office:</strong> {registered_office}</span>'
           if registered_office else '')
        + (f'<span>{contact_line}</span>' if contact_line else '')
        + (f'<span style="font-size:8px; color:#888;">{id_line}</span>'
           if id_line else '')
        + '</div></div>'
    )


def _letterhead_footer(
    *, company_name: str, cin: str, color: str, design: str,
) -> str:
    """Generate a matching footer for the letterhead design."""
    if design == "executive":
        return (
            f'<div style="margin-top:40px; padding-top:8px; '
            f'border-top:2px solid {color}; font-size:8px; color:#999; '
            f'text-align:center;">'
            f'<p style="margin:0;">{company_name}'
            + (f' &nbsp;|&nbsp; CIN: {cin}' if cin else '')
            + '</p></div>'
        )
    elif design == "formal":
        return (
            f'<div style="margin-top:40px; padding:6px; '
            f'border:1px solid {color}; font-size:8px; color:#888; '
            f'text-align:center;">'
            f'<p style="margin:0;">{company_name}'
            + (f' (CIN: {cin})' if cin else '')
            + '</p></div>'
        )
    else:
        return (
            f'<div style="margin-top:40px; padding-top:8px; '
            f'border-top:1px solid #ddd; font-size:8px; color:#aaa; '
            f'text-align:center;">'
            f'<p style="margin:0;">{company_name}'
            + (f' &nbsp;&middot;&nbsp; CIN: {cin}' if cin else '')
            + '</p></div>'
        )


def generate_letterhead_from_company(company, **overrides) -> dict:
    """Convenience: generate letterhead from a Company ORM object.

    Pass keyword overrides to customize design, accent_color, etc.
    """
    return generate_letterhead(
        company_name=company.approved_name or "[Company Name]",
        cin=company.cin or "",
        registered_office=getattr(company, "registered_office", "") or "",
        phone=getattr(company, "phone", "") or "",
        email=getattr(company, "email", "") or "",
        website=getattr(company, "website", "") or "",
        pan=company.pan or "",
        tan=company.tan or "",
        **overrides,
    )


def base_html_wrap(
    title: str,
    body: str,
    date: str = "",
    state: Optional[str] = None,
    entity_type: Optional[str] = None,
    letterhead: Optional[dict] = None,
) -> str:
    """Wrap body in a legal-compliant HTML shell with page numbers and notices.

    Args:
        title: Document title for header and page header.
        body: Inner HTML content.
        date: Optional date string (any common format, converted to DD/MM/YYYY).
        state: Optional Indian state name for state-specific stamp duty rates.
        entity_type: Optional entity type for entity-specific notices.
            One of: 'private_limited', 'opc', 'section_8', 'llp',
            'partnership', 'sole_proprietorship'.
        letterhead: Optional dict from generate_letterhead() with 'header' and
            'footer' keys. When provided, the letterhead header replaces the
            default <h1> title and the footer is appended before legal notices.
    """
    display_date = format_date_indian(date) if date else ""
    date_line = (
        f'<p class="meta">Date: {display_date}</p>'
        if display_date
        else '<p class="meta">Date: ________________________</p>'
    )
    notices = get_legal_notices(state, entity_type)

    # Letterhead replaces the default title block
    if letterhead:
        title_block = letterhead.get("header", f"<h1>{title}</h1>")
        footer_block = letterhead.get("footer", "")
    else:
        title_block = f"<h1>{title}</h1>"
        footer_block = ""

    return f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title}</title>
<style>
@page {{
    size: A4;
    margin: 2.5cm 2cm 3cm 2cm;
    @top-center {{ content: "{title}"; font-size: 8pt; color: #999; }}
    @bottom-center {{ content: "Page " counter(page) " of " counter(pages); font-size: 8pt; color: #999; }}
    @bottom-right {{ content: "Anvils"; font-size: 8pt; color: #bbb; }}
}}
body{{font-family:'Georgia','Times New Roman',serif;line-height:1.8;color:#1a1a1a;max-width:800px;margin:0 auto;padding:40px;position:relative;}}
body::before {{
    content: "DRAFT";
    position: fixed;
    top: 45%;
    left: 50%;
    transform: translate(-50%, -50%) rotate(-45deg);
    font-size: 100pt;
    font-family: 'Helvetica Neue', Arial, sans-serif;
    font-weight: bold;
    color: rgba(200, 200, 200, 0.12);
    z-index: -1;
    pointer-events: none;
    letter-spacing: 20px;
}}
h1{{font-family:'Helvetica Neue',Arial,sans-serif;font-size:24px;text-align:center;border-bottom:2px solid #333;padding-bottom:15px;margin-bottom:30px;}}
h2{{font-family:'Helvetica Neue',Arial,sans-serif;font-size:16px;margin-top:30px;color:#222;text-transform:uppercase;letter-spacing:1px;}}
.clause{{margin:15px 0;padding:10px 0;border-bottom:1px solid #eee;}}
.clause-number{{font-weight:bold;margin-right:8px;}}
.parties{{background:#f8f8f8;padding:20px;border-radius:8px;margin:20px 0;}}
.signature-block{{margin-top:60px;page-break-inside:avoid;}}
.signature-line{{margin:30px 0;}}
.signature-line .line{{border-bottom:1px solid #333;width:300px;margin-bottom:5px;}}
.meta{{text-align:center;color:#666;font-size:13px;margin-bottom:30px;}}
table{{width:100%;border-collapse:collapse;margin:20px 0;}}
th,td{{border:1px solid #ccc;padding:10px;text-align:left;}}
th{{background:#f0f0f0;font-weight:bold;}}
.witness-block{{margin-top:36px;page-break-inside:avoid;}}
.witness-line{{margin-top:24px;}}
.witness-line .line{{border-bottom:1px solid #555;width:60%;margin-bottom:5px;}}
.witness-line p{{margin:2px 0;font-size:10pt;color:#444;}}
.status-ok{{color:#27ae60;font-weight:bold;}}
.status-fail{{color:#e74c3c;font-weight:bold;}}
.score{{font-size:20px;font-weight:bold;text-align:center;margin:20px 0;}}
.letterhead-header{{page-break-inside:avoid;page-break-after:avoid;flex-shrink:0;}}
.letterhead-footer{{flex-shrink:0;margin-top:auto;page-break-inside:avoid;}}
.content-area{{flex:1 1 auto;overflow:visible;}}
@media print{{body{{padding:20px;}}body::before{{display:none;}}@page{{margin:2cm;size:A4;}}}}
</style>
</head><body{' style="display:flex;flex-direction:column;min-height:calc(100vh - 80px);"' if letterhead else ''}>
{('<div class="letterhead-header">' + title_block + '</div>') if letterhead else title_block}
<div class="content-area">
{date_line}
{body}
</div>
{('<div class="letterhead-footer">' + footer_block + '</div>') if letterhead else ''}
{notices}
</body></html>'''
