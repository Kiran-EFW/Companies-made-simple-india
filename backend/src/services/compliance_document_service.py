"""Compliance Document Generation Service -- generates ROC filing forms as HTML documents.

Generates: PAS-3 (Return of Allotment), MGT-14 (Filing of Resolutions), SH-7 (Increase in Share Capital).
All forms are generated as formatted HTML that can be downloaded, printed, or sent for e-sign.
"""

from typing import Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from src.models.legal_template import LegalDocument
from src.models.company import Company


class ComplianceDocumentService:
    """Generates compliance documents as HTML for ROC filings."""

    def generate_pas3(
        self,
        db: Session,
        company_id: int,
        user_id: int,
        allotment_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate PAS-3 (Return of Allotment) as HTML document.

        allotment_data should contain:
        - allottees: list of {name, shares, share_type, face_value, price_per_share}
        - total_shares_allotted: int
        - allotment_date: str (ISO format)
        - consideration_type: str (cash/other)
        """
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            return {"error": "Company not found"}

        company_name = company.company_name or f"Company #{company_id}"
        cin = getattr(company, "cin", "") or ""

        allottees = allotment_data.get("allottees", [])
        total_shares = allotment_data.get("total_shares_allotted", 0)
        allotment_date = allotment_data.get(
            "allotment_date",
            datetime.now(timezone.utc).strftime("%d %B %Y"),
        )

        # Build allottee rows
        allottee_rows = ""
        for i, a in enumerate(allottees, 1):
            allottee_rows += f"""
            <tr>
                <td style="border:1px solid #999;padding:8px;">{i}</td>
                <td style="border:1px solid #999;padding:8px;">{a.get('name', '')}</td>
                <td style="border:1px solid #999;padding:8px;">{a.get('shares', 0):,}</td>
                <td style="border:1px solid #999;padding:8px;">{a.get('share_type', 'Equity').title()}</td>
                <td style="border:1px solid #999;padding:8px;">&#8377;{a.get('face_value', 10)}</td>
                <td style="border:1px solid #999;padding:8px;">&#8377;{a.get('price_per_share', 10)}</td>
                <td style="border:1px solid #999;padding:8px;">&#8377;{a.get('shares', 0) * a.get('price_per_share', 10):,.2f}</td>
            </tr>"""

        total_consideration = sum(
            a.get("shares", 0) * a.get("price_per_share", 10) for a in allottees
        )

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>PAS-3 -- Return of Allotment</title>
    <style>
        body {{ font-family: 'Times New Roman', serif; margin: 40px; line-height: 1.6; color: #1a1a1a; }}
        .form-header {{ text-align: center; margin-bottom: 30px; }}
        .form-title {{ font-size: 18pt; font-weight: bold; }}
        .form-subtitle {{ font-size: 12pt; color: #555; }}
        .section {{ margin: 20px 0; }}
        .section h3 {{ border-bottom: 2px solid #333; padding-bottom: 5px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
        th {{ background: #f0f0f0; border: 1px solid #999; padding: 8px; text-align: left; }}
        .field-row {{ display: flex; margin: 8px 0; }}
        .field-label {{ width: 250px; font-weight: bold; }}
        .field-value {{ flex: 1; border-bottom: 1px dotted #999; padding-left: 10px; }}
        .signature-section {{ margin-top: 60px; display: flex; justify-content: space-between; }}
        .sig-block {{ text-align: center; width: 200px; }}
        .sig-line {{ border-top: 1px solid #333; margin-top: 60px; padding-top: 5px; font-size: 11px; }}
        .footer {{ margin-top: 30px; padding-top: 15px; border-top: 1px solid #ccc; font-size: 9pt; color: #666; text-align: center; }}
        @media print {{ body {{ margin: 20mm; }} }}
    </style>
</head>
<body>
    <div class="form-header">
        <div class="form-title">FORM PAS-3</div>
        <div class="form-subtitle">Return of Allotment</div>
        <div class="form-subtitle">[Pursuant to Section 39(4) and Rule 12 of the Companies (Prospectus and Allotment of Securities) Rules, 2014]</div>
    </div>

    <div class="section">
        <h3>1. Company Details</h3>
        <div class="field-row"><span class="field-label">Company Name:</span><span class="field-value">{company_name}</span></div>
        <div class="field-row"><span class="field-label">CIN:</span><span class="field-value">{cin}</span></div>
        <div class="field-row"><span class="field-label">Date of Allotment:</span><span class="field-value">{allotment_date}</span></div>
    </div>

    <div class="section">
        <h3>2. Details of Securities Allotted</h3>
        <div class="field-row"><span class="field-label">Total Shares Allotted:</span><span class="field-value">{total_shares:,}</span></div>
        <div class="field-row"><span class="field-label">Total Consideration:</span><span class="field-value">&#8377;{total_consideration:,.2f}</span></div>
        <div class="field-row"><span class="field-label">Nature of Consideration:</span><span class="field-value">{allotment_data.get('consideration_type', 'Cash').title()}</span></div>
    </div>

    <div class="section">
        <h3>3. Details of Allottees</h3>
        <table>
            <thead>
                <tr>
                    <th>S.No.</th>
                    <th>Name of Allottee</th>
                    <th>No. of Shares</th>
                    <th>Type</th>
                    <th>Face Value</th>
                    <th>Issue Price</th>
                    <th>Total Amount</th>
                </tr>
            </thead>
            <tbody>
                {allottee_rows if allottee_rows else '<tr><td colspan="7" style="text-align:center;padding:15px;">No allottees</td></tr>'}
            </tbody>
        </table>
    </div>

    <div class="section">
        <h3>4. Declaration</h3>
        <p>I/We hereby declare that the allotment of shares has been made in compliance with the provisions of the Companies Act, 2013 and the rules made thereunder.</p>
    </div>

    <div class="signature-section">
        <div class="sig-block"><div class="sig-line">Director</div></div>
        <div class="sig-block"><div class="sig-line">Company Secretary</div></div>
    </div>

    <div class="footer">
        <p>This form must be filed with the Registrar of Companies within 15 days of allotment.</p>
        <p>Generated on {datetime.now(timezone.utc).strftime('%d %B %Y at %H:%M UTC')}</p>
    </div>
</body>
</html>"""

        # Store as LegalDocument
        doc = LegalDocument(
            user_id=user_id,
            company_id=company_id,
            template_type="pas_3",
            title=f"PAS-3 -- Return of Allotment -- {allotment_date}",
            generated_html=html,
            status="finalized",
        )
        db.add(doc)
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
        db.refresh(doc)

        return {
            "document_id": doc.id,
            "title": doc.title,
            "template_type": "pas_3",
            "filing_deadline": "Within 15 days of allotment",
            "fee": 200,
        }

    def generate_mgt14(
        self,
        db: Session,
        company_id: int,
        user_id: int,
        resolution_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate MGT-14 (Filing of Resolutions) as HTML document.

        resolution_data should contain:
        - resolution_type: str (ordinary/special/board)
        - resolution_text: str
        - passed_at: str (meeting type -- board_meeting, agm, egm)
        - meeting_date: str
        - resolution_number: str (optional)
        """
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            return {"error": "Company not found"}

        company_name = company.company_name or f"Company #{company_id}"
        cin = getattr(company, "cin", "") or ""

        res_type = resolution_data.get("resolution_type", "special").title()
        res_text = resolution_data.get("resolution_text", "")
        passed_at = resolution_data.get("passed_at", "board_meeting").replace("_", " ").title()
        meeting_date = resolution_data.get("meeting_date", "")
        res_number = resolution_data.get("resolution_number", "")

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MGT-14 -- Filing of Resolutions</title>
    <style>
        body {{ font-family: 'Times New Roman', serif; margin: 40px; line-height: 1.6; }}
        .form-header {{ text-align: center; margin-bottom: 30px; }}
        .form-title {{ font-size: 18pt; font-weight: bold; }}
        .form-subtitle {{ font-size: 12pt; color: #555; }}
        .section {{ margin: 20px 0; }}
        .section h3 {{ border-bottom: 2px solid #333; padding-bottom: 5px; }}
        .field-row {{ display: flex; margin: 8px 0; }}
        .field-label {{ width: 250px; font-weight: bold; }}
        .field-value {{ flex: 1; border-bottom: 1px dotted #999; padding-left: 10px; }}
        .resolution-text {{ border: 1px solid #ccc; padding: 20px; margin: 15px 0; background: #fafafa; font-style: italic; }}
        .signature-section {{ margin-top: 60px; display: flex; justify-content: space-between; }}
        .sig-block {{ text-align: center; width: 200px; }}
        .sig-line {{ border-top: 1px solid #333; margin-top: 60px; padding-top: 5px; font-size: 11px; }}
        .footer {{ margin-top: 30px; padding-top: 15px; border-top: 1px solid #ccc; font-size: 9pt; color: #666; text-align: center; }}
        @media print {{ body {{ margin: 20mm; }} }}
    </style>
</head>
<body>
    <div class="form-header">
        <div class="form-title">FORM MGT-14</div>
        <div class="form-subtitle">Filing of Resolutions and Agreements</div>
        <div class="form-subtitle">[Pursuant to Section 117(1) of the Companies Act, 2013 and Rule 15 of the Companies (Management and Administration) Rules, 2014]</div>
    </div>

    <div class="section">
        <h3>1. Company Details</h3>
        <div class="field-row"><span class="field-label">Company Name:</span><span class="field-value">{company_name}</span></div>
        <div class="field-row"><span class="field-label">CIN:</span><span class="field-value">{cin}</span></div>
    </div>

    <div class="section">
        <h3>2. Resolution Details</h3>
        <div class="field-row"><span class="field-label">Resolution Type:</span><span class="field-value">{res_type} Resolution</span></div>
        <div class="field-row"><span class="field-label">Resolution Number:</span><span class="field-value">{res_number or 'N/A'}</span></div>
        <div class="field-row"><span class="field-label">Passed At:</span><span class="field-value">{passed_at}</span></div>
        <div class="field-row"><span class="field-label">Date of Meeting:</span><span class="field-value">{meeting_date}</span></div>
    </div>

    <div class="section">
        <h3>3. Text of Resolution</h3>
        <div class="resolution-text">{res_text or '[Resolution text to be inserted]'}</div>
    </div>

    <div class="section">
        <h3>4. Declaration</h3>
        <p>I/We hereby declare that the resolution was duly passed in accordance with the provisions of the Companies Act, 2013.</p>
    </div>

    <div class="signature-section">
        <div class="sig-block"><div class="sig-line">Director</div></div>
        <div class="sig-block"><div class="sig-line">Company Secretary</div></div>
    </div>

    <div class="footer">
        <p>This form must be filed with the Registrar of Companies within 30 days of passing the resolution.</p>
        <p>Generated on {datetime.now(timezone.utc).strftime('%d %B %Y at %H:%M UTC')}</p>
    </div>
</body>
</html>"""

        doc = LegalDocument(
            user_id=user_id,
            company_id=company_id,
            template_type="mgt_14",
            title=f"MGT-14 -- {res_type} Resolution -- {meeting_date}",
            generated_html=html,
            status="finalized",
        )
        db.add(doc)
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
        db.refresh(doc)

        return {
            "document_id": doc.id,
            "title": doc.title,
            "template_type": "mgt_14",
            "filing_deadline": "Within 30 days of passing the resolution",
            "fee": 200,
        }

    def generate_sh7(
        self,
        db: Session,
        company_id: int,
        user_id: int,
        capital_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate SH-7 (Notice of Increase in Share Capital) as HTML document.

        capital_data should contain:
        - existing_authorized_capital: float
        - new_authorized_capital: float
        - increase_amount: float
        - resolution_date: str
        - share_details: list of {share_type, number_of_shares, face_value}
        """
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            return {"error": "Company not found"}

        company_name = company.company_name or f"Company #{company_id}"
        cin = getattr(company, "cin", "") or ""

        existing = capital_data.get("existing_authorized_capital", 0)
        new_capital = capital_data.get("new_authorized_capital", 0)
        increase = capital_data.get("increase_amount", new_capital - existing)
        res_date = capital_data.get("resolution_date", "")
        share_details = capital_data.get("share_details", [])

        share_rows = ""
        for i, sd in enumerate(share_details, 1):
            share_rows += f"""
            <tr>
                <td style="border:1px solid #999;padding:8px;">{i}</td>
                <td style="border:1px solid #999;padding:8px;">{sd.get('share_type', 'Equity').title()}</td>
                <td style="border:1px solid #999;padding:8px;">{sd.get('number_of_shares', 0):,}</td>
                <td style="border:1px solid #999;padding:8px;">&#8377;{sd.get('face_value', 10)}</td>
                <td style="border:1px solid #999;padding:8px;">&#8377;{sd.get('number_of_shares', 0) * sd.get('face_value', 10):,.2f}</td>
            </tr>"""

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SH-7 -- Notice to Registrar of Increase in Share Capital</title>
    <style>
        body {{ font-family: 'Times New Roman', serif; margin: 40px; line-height: 1.6; }}
        .form-header {{ text-align: center; margin-bottom: 30px; }}
        .form-title {{ font-size: 18pt; font-weight: bold; }}
        .form-subtitle {{ font-size: 12pt; color: #555; }}
        .section {{ margin: 20px 0; }}
        .section h3 {{ border-bottom: 2px solid #333; padding-bottom: 5px; }}
        table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
        th {{ background: #f0f0f0; border: 1px solid #999; padding: 8px; text-align: left; }}
        .field-row {{ display: flex; margin: 8px 0; }}
        .field-label {{ width: 300px; font-weight: bold; }}
        .field-value {{ flex: 1; border-bottom: 1px dotted #999; padding-left: 10px; }}
        .capital-box {{ border: 2px solid #333; padding: 20px; margin: 15px 0; background: #f9f9f9; }}
        .signature-section {{ margin-top: 60px; display: flex; justify-content: space-between; }}
        .sig-block {{ text-align: center; width: 200px; }}
        .sig-line {{ border-top: 1px solid #333; margin-top: 60px; padding-top: 5px; font-size: 11px; }}
        .footer {{ margin-top: 30px; padding-top: 15px; border-top: 1px solid #ccc; font-size: 9pt; color: #666; text-align: center; }}
        @media print {{ body {{ margin: 20mm; }} }}
    </style>
</head>
<body>
    <div class="form-header">
        <div class="form-title">FORM SH-7</div>
        <div class="form-subtitle">Notice to Registrar of any Alteration of Share Capital</div>
        <div class="form-subtitle">[Pursuant to Section 64(1) of the Companies Act, 2013 and Rule 15 of the Companies (Share Capital and Debentures) Rules, 2014]</div>
    </div>

    <div class="section">
        <h3>1. Company Details</h3>
        <div class="field-row"><span class="field-label">Company Name:</span><span class="field-value">{company_name}</span></div>
        <div class="field-row"><span class="field-label">CIN:</span><span class="field-value">{cin}</span></div>
    </div>

    <div class="section">
        <h3>2. Capital Details</h3>
        <div class="capital-box">
            <div class="field-row"><span class="field-label">Existing Authorized Capital:</span><span class="field-value">&#8377;{existing:,.2f}</span></div>
            <div class="field-row"><span class="field-label">Increase in Capital:</span><span class="field-value">&#8377;{increase:,.2f}</span></div>
            <div class="field-row"><span class="field-label">New Authorized Capital:</span><span class="field-value">&#8377;{new_capital:,.2f}</span></div>
            <div class="field-row"><span class="field-label">Date of Resolution:</span><span class="field-value">{res_date}</span></div>
        </div>
    </div>

    <div class="section">
        <h3>3. Details of Shares</h3>
        <table>
            <thead>
                <tr>
                    <th>S.No.</th>
                    <th>Type of Shares</th>
                    <th>Number of Shares</th>
                    <th>Face Value</th>
                    <th>Total Value</th>
                </tr>
            </thead>
            <tbody>
                {share_rows if share_rows else '<tr><td colspan="5" style="text-align:center;padding:15px;">No details</td></tr>'}
            </tbody>
        </table>
    </div>

    <div class="section">
        <h3>4. Declaration</h3>
        <p>I/We hereby declare that the increase in share capital has been authorized by an ordinary/special resolution passed at the general meeting of the company.</p>
    </div>

    <div class="signature-section">
        <div class="sig-block"><div class="sig-line">Director</div></div>
        <div class="sig-block"><div class="sig-line">Company Secretary</div></div>
    </div>

    <div class="footer">
        <p>This form must be filed with the Registrar of Companies within 30 days of the resolution authorizing the increase.</p>
        <p>Generated on {datetime.now(timezone.utc).strftime('%d %B %Y at %H:%M UTC')}</p>
    </div>
</body>
</html>"""

        doc = LegalDocument(
            user_id=user_id,
            company_id=company_id,
            template_type="sh_7",
            title=f"SH-7 -- Increase in Share Capital -- {res_date}",
            generated_html=html,
            status="finalized",
        )
        db.add(doc)
        try:
            db.commit()
        except Exception:
            db.rollback()
            raise
        db.refresh(doc)

        return {
            "document_id": doc.id,
            "title": doc.title,
            "template_type": "sh_7",
            "filing_deadline": "Within 30 days of passing the resolution",
            "fee": 200,
        }


# Singleton
compliance_document_service = ComplianceDocumentService()
