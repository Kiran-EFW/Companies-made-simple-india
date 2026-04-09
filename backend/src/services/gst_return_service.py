"""GST Return JSON generation service.

Generates GSTN-schema-compliant JSON for:
  - GSTR-1: Outward supply statement (monthly/quarterly)
  - GSTR-3B: Summary return

JSON schemas follow GSTN API specifications for ASP/GSP integration.

References:
  - CGST Act 2017, Section 37 (GSTR-1), Section 39 (GSTR-3B)
  - GSTN API v3.0 specifications
  - HSN code structure per Customs Tariff Act 1975
"""

import re
import logging
from datetime import datetime
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# GSTIN validation
# ---------------------------------------------------------------------------

_GSTIN_RE = re.compile(
    r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[A-Z0-9]{1}Z[A-Z0-9]{1}$"
)

# State codes (first 2 digits of GSTIN)
STATE_CODES: dict[str, str] = {
    "01": "Jammu & Kashmir", "02": "Himachal Pradesh", "03": "Punjab",
    "04": "Chandigarh", "05": "Uttarakhand", "06": "Haryana",
    "07": "Delhi", "08": "Rajasthan", "09": "Uttar Pradesh",
    "10": "Bihar", "11": "Sikkim", "12": "Arunachal Pradesh",
    "13": "Nagaland", "14": "Manipur", "15": "Mizoram",
    "16": "Tripura", "17": "Meghalaya", "18": "Assam",
    "19": "West Bengal", "20": "Jharkhand", "21": "Odisha",
    "22": "Chhattisgarh", "23": "Madhya Pradesh", "24": "Gujarat",
    "25": "Daman & Diu", "26": "Dadra & Nagar Haveli",
    "27": "Maharashtra", "28": "Andhra Pradesh (Old)",
    "29": "Karnataka", "30": "Goa", "32": "Kerala",
    "33": "Tamil Nadu", "34": "Puducherry", "35": "Andaman & Nicobar",
    "36": "Telangana", "37": "Andhra Pradesh", "38": "Ladakh",
    "96": "Foreign Country", "97": "Other Territory",
}


def validate_gstin(gstin: str) -> dict:
    """Validate GSTIN format. Returns dict with 'valid', 'state_code', 'state'."""
    gstin = gstin.strip().upper()
    if not _GSTIN_RE.match(gstin):
        return {"valid": False, "error": "Invalid GSTIN format"}
    sc = gstin[:2]
    state = STATE_CODES.get(sc)
    if not state:
        return {"valid": False, "error": f"Unknown state code: {sc}"}
    return {"valid": True, "gstin": gstin, "state_code": sc, "state": state}


def get_state_code(gstin: str) -> str:
    """Extract 2-digit state code from GSTIN."""
    return gstin[:2] if gstin and len(gstin) >= 2 else ""


# ---------------------------------------------------------------------------
# GSTR-1 JSON generation
# ---------------------------------------------------------------------------

class GSTR1Builder:
    """Build GSTR-1 JSON from transaction data.

    GSTR-1 is the outward supply statement filed under Section 37 of
    CGST Act 2017. Due by the 11th of the following month (monthly filers)
    or 13th of month after quarter (QRMP scheme).

    GSTN JSON structure:
        gstin, fp (filing period MMYYYY), b2b, b2cl, b2cs, cdnr, cdnur,
        exp, hsn, nil, doc_issue
    """

    def __init__(self, gstin: str, filing_period: str):
        """
        Args:
            gstin: Supplier GSTIN (15-char).
            filing_period: Filing period as MMYYYY (e.g., '042025' for April 2025).
        """
        self.gstin = gstin.strip().upper()
        self.fp = filing_period
        self._b2b: dict[str, list] = {}       # GSTIN -> list of invoices
        self._b2cl: dict[str, list] = {}      # POS state code -> invoices
        self._b2cs: list[dict] = []
        self._cdnr: dict[str, list] = {}      # GSTIN -> credit/debit notes
        self._cdnur: list[dict] = []
        self._exp: list[dict] = []
        self._hsn: dict[str, dict] = {}       # HSN code -> aggregated data
        self._nil: list[dict] = []
        self._docs: list[dict] = []

    # -- B2B: Registered recipients (invoice value > 0) --

    def add_b2b_invoice(
        self,
        *,
        recipient_gstin: str,
        invoice_number: str,
        invoice_date: str,
        invoice_value: float,
        place_of_supply: str,
        reverse_charge: bool = False,
        invoice_type: str = "R",
        items: list[dict],
    ) -> None:
        """Add a B2B (business-to-business) invoice.

        Args:
            recipient_gstin: Buyer's GSTIN.
            invoice_number: Invoice number (max 16 chars).
            invoice_date: Date as DD-MM-YYYY.
            invoice_value: Total invoice value including tax.
            place_of_supply: 2-digit state code (e.g., '29' for Karnataka).
            reverse_charge: Whether reverse charge applies.
            invoice_type: 'R' (Regular), 'DE' (Deemed Export), 'SEWP' (SEZ with payment),
                         'SEWOP' (SEZ without payment).
            items: List of line items, each with keys:
                rate (GST rate: 0, 0.25, 3, 5, 12, 18, 28),
                taxable_value, cess (optional).
        """
        inv = {
            "inum": invoice_number[:16],
            "idt": invoice_date,
            "val": round(invoice_value, 2),
            "pos": place_of_supply,
            "rchrg": "Y" if reverse_charge else "N",
            "inv_typ": invoice_type,
            "itms": [self._build_item(it) for it in items],
        }
        self._b2b.setdefault(recipient_gstin.upper(), []).append(inv)

    # -- B2CL: Unregistered recipients, inter-state, value > 2.5 lakh --

    def add_b2cl_invoice(
        self,
        *,
        invoice_number: str,
        invoice_date: str,
        invoice_value: float,
        place_of_supply: str,
        items: list[dict],
    ) -> None:
        """Add a B2CL invoice (unregistered, inter-state, > Rs 2.5 lakh)."""
        inv = {
            "inum": invoice_number[:16],
            "idt": invoice_date,
            "val": round(invoice_value, 2),
            "itms": [self._build_item(it) for it in items],
        }
        self._b2cl.setdefault(place_of_supply, []).append(inv)

    # -- B2CS: Unregistered recipients (intra-state, or inter-state <= 2.5L) --

    def add_b2cs(
        self,
        *,
        place_of_supply: str,
        supply_type: str = "INTRA",
        rate: float,
        taxable_value: float,
        cess: float = 0,
    ) -> None:
        """Add B2CS summary entry (aggregated by rate + POS + type)."""
        self._b2cs.append({
            "sply_ty": supply_type,  # INTRA or INTER
            "pos": place_of_supply,
            "rt": rate,
            "txval": round(taxable_value, 2),
            "camt": round(taxable_value * rate / 200, 2) if supply_type == "INTRA" else 0,
            "samt": round(taxable_value * rate / 200, 2) if supply_type == "INTRA" else 0,
            "iamt": round(taxable_value * rate / 100, 2) if supply_type == "INTER" else 0,
            "csamt": round(cess, 2),
        })

    # -- CDNR: Credit/debit notes for registered recipients --

    def add_credit_debit_note(
        self,
        *,
        recipient_gstin: str,
        note_number: str,
        note_date: str,
        note_type: str,
        original_invoice_number: str,
        original_invoice_date: str,
        note_value: float,
        items: list[dict],
    ) -> None:
        """Add a credit/debit note for a registered recipient.

        Args:
            note_type: 'C' (Credit) or 'D' (Debit).
        """
        note = {
            "ntty": note_type,
            "nt_num": note_number[:16],
            "nt_dt": note_date,
            "val": round(note_value, 2),
            "p_gst": "N",
            "inum": original_invoice_number,
            "idt": original_invoice_date,
            "itms": [self._build_item(it) for it in items],
        }
        self._cdnr.setdefault(recipient_gstin.upper(), []).append(note)

    # -- Exports --

    def add_export(
        self,
        *,
        invoice_number: str,
        invoice_date: str,
        invoice_value: float,
        port_code: str = "",
        shipping_bill_number: str = "",
        shipping_bill_date: str = "",
        export_type: str = "WPAY",
        items: list[dict],
    ) -> None:
        """Add an export invoice.

        Args:
            export_type: 'WPAY' (with payment of tax) or 'WOPAY' (without).
        """
        exp = {
            "exp_typ": export_type,
            "inum": invoice_number[:16],
            "idt": invoice_date,
            "val": round(invoice_value, 2),
            "sbpcode": port_code,
            "sbnum": shipping_bill_number,
            "sbdt": shipping_bill_date,
            "itms": [self._build_item(it) for it in items],
        }
        self._exp.append(exp)

    # -- HSN Summary --

    def add_hsn_entry(
        self,
        *,
        hsn_code: str,
        description: str = "",
        uqc: str = "NOS",
        quantity: float = 0,
        taxable_value: float = 0,
        igst: float = 0,
        cgst: float = 0,
        sgst: float = 0,
        cess: float = 0,
        total_value: float = 0,
    ) -> None:
        """Add or aggregate an HSN summary entry.

        Args:
            uqc: Unit Quantity Code — NOS (Numbers), KGS, MTR, LTR, SQM, etc.
        """
        key = hsn_code
        if key in self._hsn:
            existing = self._hsn[key]
            existing["qty"] += quantity
            existing["txval"] += taxable_value
            existing["iamt"] += igst
            existing["camt"] += cgst
            existing["samt"] += sgst
            existing["csamt"] += cess
            existing["val"] += total_value
        else:
            self._hsn[key] = {
                "hsn_sc": hsn_code,
                "desc": description,
                "uqc": uqc,
                "qty": quantity,
                "txval": taxable_value,
                "iamt": igst,
                "camt": cgst,
                "samt": sgst,
                "csamt": cess,
                "val": total_value,
            }

    # -- Nil / Exempt / Non-GST --

    def add_nil_supply(
        self,
        *,
        supply_type: str,
        nil_amount: float = 0,
        exempt_amount: float = 0,
        non_gst_amount: float = 0,
    ) -> None:
        """Add nil/exempt/non-GST supply entry.

        Args:
            supply_type: 'INTRB2B', 'INTRB2C', 'INTRAB2B', 'INTRAB2C'.
        """
        self._nil.append({
            "sply_ty": supply_type,
            "nil_amt": round(nil_amount, 2),
            "expt_amt": round(exempt_amount, 2),
            "ngsup_amt": round(non_gst_amount, 2),
        })

    # -- Document Issue Summary --

    def add_doc_issue(
        self,
        *,
        doc_type: int = 1,
        doc_name: str = "Invoices for outward supply",
        from_serial: str = "",
        to_serial: str = "",
        total_issued: int = 0,
        total_cancelled: int = 0,
    ) -> None:
        """Add document issue summary.

        Args:
            doc_type: 1=Invoices, 2=Delivery Challan, 3=Debit Note,
                     4=Credit Note, 5=Receipt Voucher, etc.
        """
        self._docs.append({
            "doc_typ": doc_type,
            "doc_nm": doc_name,
            "docs": [{
                "num": 1,
                "from": from_serial,
                "to": to_serial,
                "totnum": total_issued,
                "cancel": total_cancelled,
                "net_issue": total_issued - total_cancelled,
            }],
        })

    # -- Build final JSON --

    def build(self) -> dict:
        """Build the complete GSTR-1 JSON payload."""
        result: dict[str, Any] = {
            "gstin": self.gstin,
            "fp": self.fp,
        }

        # B2B
        if self._b2b:
            result["b2b"] = [
                {"ctin": gstin, "inv": invoices}
                for gstin, invoices in self._b2b.items()
            ]

        # B2CL
        if self._b2cl:
            result["b2cl"] = [
                {"pos": pos, "inv": invoices}
                for pos, invoices in self._b2cl.items()
            ]

        # B2CS
        if self._b2cs:
            result["b2cs"] = self._b2cs

        # CDNR
        if self._cdnr:
            result["cdnr"] = [
                {"ctin": gstin, "nt": notes}
                for gstin, notes in self._cdnr.items()
            ]

        # CDNUR
        if self._cdnur:
            result["cdnur"] = self._cdnur

        # Exports
        if self._exp:
            result["exp"] = self._exp

        # HSN Summary
        if self._hsn:
            result["hsn"] = {
                "data": [
                    {k: round(v, 2) if isinstance(v, float) else v
                     for k, v in entry.items()}
                    for entry in self._hsn.values()
                ]
            }

        # Nil / Exempt
        if self._nil:
            result["nil"] = {"inv": self._nil}

        # Document Issue
        if self._docs:
            result["doc_issue"] = {"doc_det": self._docs}

        return result

    # -- Internal helpers --

    @staticmethod
    def _build_item(item: dict) -> dict:
        """Convert a line item dict to GSTN item format."""
        rate = item.get("rate", 18)
        txval = round(item.get("taxable_value", 0), 2)
        cess = round(item.get("cess", 0), 2)
        return {
            "num": item.get("num", 1),
            "itm_det": {
                "rt": rate,
                "txval": txval,
                "iamt": round(txval * rate / 100, 2),
                "csamt": cess,
            },
        }


# ---------------------------------------------------------------------------
# GSTR-3B JSON generation
# ---------------------------------------------------------------------------

class GSTR3BBuilder:
    """Build GSTR-3B summary JSON.

    GSTR-3B is the monthly/quarterly summary return under Section 39 of
    CGST Act 2017. Due by the 20th of the following month (monthly filers)
    or staggered dates for quarterly filers.

    Tables:
        3.1: Outward supplies and inward supplies (reverse charge)
        3.2: Inter-state supplies to unregistered persons, composition
             dealers, and UIN holders
        4:   Eligible ITC
        5:   Exempt, nil-rated, and non-GST inward supplies
        6.1: Payment of tax
    """

    def __init__(self, gstin: str, filing_period: str):
        self.gstin = gstin.strip().upper()
        self.fp = filing_period
        # Table 3.1 — Outward supplies
        self._t31 = {
            "osup_det": {"txval": 0, "iamt": 0, "camt": 0, "samt": 0, "csamt": 0},
            "osup_zero": {"txval": 0, "iamt": 0, "camt": 0, "samt": 0, "csamt": 0},
            "osup_nil_exmp": {"txval": 0, "iamt": 0, "camt": 0, "samt": 0, "csamt": 0},
            "isup_rev": {"txval": 0, "iamt": 0, "camt": 0, "samt": 0, "csamt": 0},
            "osup_nongst": {"txval": 0, "iamt": 0, "camt": 0, "samt": 0, "csamt": 0},
        }
        # Table 3.2 — Inter-state supplies
        self._t32 = {
            "unreg_details": [],
            "comp_details": [],
            "uin_details": [],
        }
        # Table 4 — ITC
        self._t4 = {
            "itc_avl": [
                {"ty": "IMPG", "iamt": 0, "camt": 0, "samt": 0, "csamt": 0},
                {"ty": "IMPS", "iamt": 0, "camt": 0, "samt": 0, "csamt": 0},
                {"ty": "ISRC", "iamt": 0, "camt": 0, "samt": 0, "csamt": 0},
                {"ty": "ISD", "iamt": 0, "camt": 0, "samt": 0, "csamt": 0},
                {"ty": "OTH", "iamt": 0, "camt": 0, "samt": 0, "csamt": 0},
            ],
            "itc_rev": [
                {"ty": "RUL", "iamt": 0, "camt": 0, "samt": 0, "csamt": 0},
                {"ty": "OTH", "iamt": 0, "camt": 0, "samt": 0, "csamt": 0},
            ],
            "itc_net": {"iamt": 0, "camt": 0, "samt": 0, "csamt": 0},
            "itc_inelg": [
                {"ty": "RUL", "iamt": 0, "camt": 0, "samt": 0, "csamt": 0},
                {"ty": "OTH", "iamt": 0, "camt": 0, "samt": 0, "csamt": 0},
            ],
        }
        # Table 5 — Exempt supplies
        self._t5 = {
            "isup_details": [
                {"ty": "ISRC", "inter": 0, "intra": 0},
                {"ty": "ISRC_REV", "inter": 0, "intra": 0},
                {"ty": "ISD", "inter": 0, "intra": 0},
            ],
        }
        # Table 6.1 — Payment
        self._t61 = {
            "igst": {"tx_i": 0, "tx_cs": 0},
            "cgst": {"tx_i": 0, "tx_cs": 0},
            "sgst": {"tx_i": 0, "tx_cs": 0},
            "cess": {"tx_i": 0, "tx_cs": 0},
        }

    # -- Table 3.1: Outward supplies --

    def set_outward_taxable(
        self, *, taxable_value: float, igst: float = 0,
        cgst: float = 0, sgst: float = 0, cess: float = 0,
    ) -> None:
        """Set Table 3.1(a): Outward taxable supplies (other than zero/nil)."""
        self._t31["osup_det"] = {
            "txval": round(taxable_value, 2),
            "iamt": round(igst, 2),
            "camt": round(cgst, 2),
            "samt": round(sgst, 2),
            "csamt": round(cess, 2),
        }

    def set_outward_zero_rated(
        self, *, taxable_value: float, igst: float = 0, cess: float = 0,
    ) -> None:
        """Set Table 3.1(b): Outward zero-rated supplies."""
        self._t31["osup_zero"] = {
            "txval": round(taxable_value, 2),
            "iamt": round(igst, 2),
            "camt": 0, "samt": 0,
            "csamt": round(cess, 2),
        }

    def set_outward_nil_exempt(self, *, taxable_value: float) -> None:
        """Set Table 3.1(c): Nil rated, exempted supplies."""
        self._t31["osup_nil_exmp"] = {
            "txval": round(taxable_value, 2),
            "iamt": 0, "camt": 0, "samt": 0, "csamt": 0,
        }

    def set_inward_reverse_charge(
        self, *, taxable_value: float, igst: float = 0,
        cgst: float = 0, sgst: float = 0, cess: float = 0,
    ) -> None:
        """Set Table 3.1(d): Inward supplies (reverse charge)."""
        self._t31["isup_rev"] = {
            "txval": round(taxable_value, 2),
            "iamt": round(igst, 2),
            "camt": round(cgst, 2),
            "samt": round(sgst, 2),
            "csamt": round(cess, 2),
        }

    def set_non_gst_outward(self, *, taxable_value: float) -> None:
        """Set Table 3.1(e): Non-GST outward supplies."""
        self._t31["osup_nongst"] = {
            "txval": round(taxable_value, 2),
            "iamt": 0, "camt": 0, "samt": 0, "csamt": 0,
        }

    # -- Table 3.2: Inter-state supplies to unregistered --

    def add_interstate_unreg(
        self, *, place_of_supply: str, taxable_value: float, igst: float,
    ) -> None:
        """Add Table 3.2(a): Inter-state supplies to unregistered persons."""
        self._t32["unreg_details"].append({
            "pos": place_of_supply,
            "txval": round(taxable_value, 2),
            "iamt": round(igst, 2),
        })

    # -- Table 4: ITC --

    def set_itc(
        self,
        *,
        itc_type: str = "OTH",
        igst: float = 0,
        cgst: float = 0,
        sgst: float = 0,
        cess: float = 0,
    ) -> None:
        """Set available ITC by type.

        Args:
            itc_type: 'IMPG' (Import of Goods), 'IMPS' (Import of Services),
                     'ISRC' (Inward supplies reverse charge), 'ISD' (Input Service
                     Distributor), 'OTH' (All other ITC).
        """
        for entry in self._t4["itc_avl"]:
            if entry["ty"] == itc_type:
                entry["iamt"] = round(igst, 2)
                entry["camt"] = round(cgst, 2)
                entry["samt"] = round(sgst, 2)
                entry["csamt"] = round(cess, 2)
                break
        self._recalculate_net_itc()

    def set_itc_reversed(
        self,
        *,
        reversal_type: str = "OTH",
        igst: float = 0,
        cgst: float = 0,
        sgst: float = 0,
        cess: float = 0,
    ) -> None:
        """Set ITC reversed.

        Args:
            reversal_type: 'RUL' (As per rules) or 'OTH' (Other).
        """
        for entry in self._t4["itc_rev"]:
            if entry["ty"] == reversal_type:
                entry["iamt"] = round(igst, 2)
                entry["camt"] = round(cgst, 2)
                entry["samt"] = round(sgst, 2)
                entry["csamt"] = round(cess, 2)
                break
        self._recalculate_net_itc()

    def set_itc_ineligible(
        self,
        *,
        ineligible_type: str = "OTH",
        igst: float = 0,
        cgst: float = 0,
        sgst: float = 0,
        cess: float = 0,
    ) -> None:
        """Set ineligible ITC.

        Args:
            ineligible_type: 'RUL' (As per Section 17(5)) or 'OTH' (Other).
        """
        for entry in self._t4["itc_inelg"]:
            if entry["ty"] == ineligible_type:
                entry["iamt"] = round(igst, 2)
                entry["camt"] = round(cgst, 2)
                entry["samt"] = round(sgst, 2)
                entry["csamt"] = round(cess, 2)
                break

    def _recalculate_net_itc(self) -> None:
        """Recalculate net ITC = available - reversed."""
        net = {"iamt": 0, "camt": 0, "samt": 0, "csamt": 0}
        for entry in self._t4["itc_avl"]:
            for k in net:
                net[k] += entry[k]
        for entry in self._t4["itc_rev"]:
            for k in net:
                net[k] -= entry[k]
        self._t4["itc_net"] = {k: round(v, 2) for k, v in net.items()}

    # -- Table 6.1: Payment --

    def set_payment(
        self, *,
        igst_payable: float = 0, igst_itc_used: float = 0,
        cgst_payable: float = 0, cgst_itc_used: float = 0,
        sgst_payable: float = 0, sgst_itc_used: float = 0,
        cess_payable: float = 0, cess_itc_used: float = 0,
    ) -> None:
        """Set Table 6.1: Payment of tax (cash + ITC)."""
        self._t61 = {
            "igst": {
                "tx_i": round(igst_itc_used, 2),
                "tx_cs": round(max(igst_payable - igst_itc_used, 0), 2),
            },
            "cgst": {
                "tx_i": round(cgst_itc_used, 2),
                "tx_cs": round(max(cgst_payable - cgst_itc_used, 0), 2),
            },
            "sgst": {
                "tx_i": round(sgst_itc_used, 2),
                "tx_cs": round(max(sgst_payable - sgst_itc_used, 0), 2),
            },
            "cess": {
                "tx_i": round(cess_itc_used, 2),
                "tx_cs": round(max(cess_payable - cess_itc_used, 0), 2),
            },
        }

    # -- Build final JSON --

    def build(self) -> dict:
        """Build the complete GSTR-3B JSON payload."""
        return {
            "gstin": self.gstin,
            "ret_period": self.fp,
            "sup_details": self._t31,
            "inter_sup": self._t32,
            "itc_elg": self._t4,
            "inward_sup": self._t5,
            "tax_pmt": self._t61,
        }


# ---------------------------------------------------------------------------
# Convenience: auto-generate from invoice list
# ---------------------------------------------------------------------------

def build_gstr1_from_invoices(
    gstin: str,
    filing_period: str,
    invoices: list[dict],
    supplier_state_code: str = "",
) -> dict:
    """Build GSTR-1 JSON from a list of invoice dicts.

    Each invoice dict should have:
        invoice_number, invoice_date (DD-MM-YYYY), invoice_value,
        recipient_gstin (empty for B2C), place_of_supply (2-digit state code),
        items: [{description, hsn_code, rate, taxable_value, quantity, uqc}],
        note_type (optional: 'C' or 'D' for credit/debit notes),
        original_invoice_number, original_invoice_date (for notes),
        is_export (optional bool), export_type (optional: 'WPAY'/'WOPAY').
    """
    if not supplier_state_code:
        supplier_state_code = get_state_code(gstin)

    builder = GSTR1Builder(gstin, filing_period)

    for inv in invoices:
        recipient = inv.get("recipient_gstin", "")
        pos = inv.get("place_of_supply", supplier_state_code)
        items = inv.get("items", [])
        inv_val = inv.get("invoice_value", 0)
        inv_num = inv.get("invoice_number", "")
        inv_date = inv.get("invoice_date", "")

        # Build GSTN item format
        gstn_items = [
            {"rate": it.get("rate", 18), "taxable_value": it.get("taxable_value", 0)}
            for it in items
        ]

        # Credit/Debit note
        if inv.get("note_type"):
            if recipient:
                builder.add_credit_debit_note(
                    recipient_gstin=recipient,
                    note_number=inv_num,
                    note_date=inv_date,
                    note_type=inv.get("note_type", "C"),
                    original_invoice_number=inv.get("original_invoice_number", ""),
                    original_invoice_date=inv.get("original_invoice_date", ""),
                    note_value=inv_val,
                    items=gstn_items,
                )
            continue

        # Export
        if inv.get("is_export"):
            builder.add_export(
                invoice_number=inv_num,
                invoice_date=inv_date,
                invoice_value=inv_val,
                export_type=inv.get("export_type", "WPAY"),
                items=gstn_items,
            )
            # HSN entries
            for it in items:
                _add_hsn_from_item(builder, it, is_interstate=True)
            continue

        # B2B: Registered recipient
        if recipient:
            builder.add_b2b_invoice(
                recipient_gstin=recipient,
                invoice_number=inv_num,
                invoice_date=inv_date,
                invoice_value=inv_val,
                place_of_supply=pos,
                items=gstn_items,
            )
            # HSN
            is_inter = pos != supplier_state_code
            for it in items:
                _add_hsn_from_item(builder, it, is_interstate=is_inter)

        # B2CL: Unregistered, inter-state, > 2.5L
        elif pos != supplier_state_code and inv_val > 250000:
            builder.add_b2cl_invoice(
                invoice_number=inv_num,
                invoice_date=inv_date,
                invoice_value=inv_val,
                place_of_supply=pos,
                items=gstn_items,
            )
            for it in items:
                _add_hsn_from_item(builder, it, is_interstate=True)

        # B2CS: Everything else
        else:
            is_inter = pos != supplier_state_code
            total_taxable = sum(it.get("taxable_value", 0) for it in items)
            rate = items[0].get("rate", 18) if items else 18
            builder.add_b2cs(
                place_of_supply=pos,
                supply_type="INTER" if is_inter else "INTRA",
                rate=rate,
                taxable_value=total_taxable,
            )
            for it in items:
                _add_hsn_from_item(builder, it, is_interstate=is_inter)

    return builder.build()


def _add_hsn_from_item(
    builder: GSTR1Builder,
    item: dict,
    is_interstate: bool,
) -> None:
    """Add HSN summary entry from an invoice item."""
    hsn = item.get("hsn_code", "")
    if not hsn:
        return
    rate = item.get("rate", 18)
    txval = item.get("taxable_value", 0)
    tax = txval * rate / 100
    builder.add_hsn_entry(
        hsn_code=hsn,
        description=item.get("description", ""),
        uqc=item.get("uqc", "NOS"),
        quantity=item.get("quantity", 1),
        taxable_value=txval,
        igst=tax if is_interstate else 0,
        cgst=tax / 2 if not is_interstate else 0,
        sgst=tax / 2 if not is_interstate else 0,
        total_value=txval + tax,
    )
