from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from src.database import get_db
from src.models.user import User
from src.models.statutory_register import StatutoryRegister, RegisterEntry
from src.schemas.statutory_register import (
    REGISTER_TYPES,
    REGISTER_DATA_FIELDS,
    RegisterEntryCreate,
    RegisterEntryUpdate,
    RegisterEntryOut,
    StatutoryRegisterOut,
    RegisterSummaryItem,
    RegisterSummaryOut,
)
from src.utils.security import get_current_user
from src.utils.tier_gate import require_tier

router = APIRouter(
    prefix="/companies/{company_id}/registers",
    tags=["statutory-registers"],
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ensure_all_registers(db: Session, company_id: int) -> List[StatutoryRegister]:
    """Auto-create all mandatory registers for company if they don't exist."""
    existing = (
        db.query(StatutoryRegister)
        .filter(StatutoryRegister.company_id == company_id)
        .all()
    )
    existing_types = {r.register_type for r in existing}
    created = list(existing)

    for rtype in REGISTER_TYPES:
        if rtype not in existing_types:
            reg = StatutoryRegister(company_id=company_id, register_type=rtype)
            db.add(reg)
            created.append(reg)

    if len(created) > len(existing):
        db.commit()
        for r in created:
            db.refresh(r)

    return created


def _get_register(db: Session, company_id: int, register_type: str) -> StatutoryRegister:
    """Fetch a register by type, auto-creating all if needed."""
    register_type = register_type.upper()
    if register_type not in REGISTER_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid register type: {register_type}. Valid types: {REGISTER_TYPES}",
        )
    _ensure_all_registers(db, company_id)
    reg = (
        db.query(StatutoryRegister)
        .filter(
            StatutoryRegister.company_id == company_id,
            StatutoryRegister.register_type == register_type,
        )
        .first()
    )
    if not reg:
        raise HTTPException(status_code=404, detail="Register not found")
    return reg


def _serialize_entry(entry: RegisterEntry) -> dict:
    return {
        "id": entry.id,
        "register_id": entry.register_id,
        "company_id": entry.company_id,
        "entry_number": entry.entry_number,
        "entry_date": entry.entry_date.isoformat() if entry.entry_date else "",
        "data": entry.data or {},
        "notes": entry.notes,
        "created_by": entry.created_by,
        "created_at": entry.created_at.isoformat() if entry.created_at else "",
        "updated_at": entry.updated_at.isoformat() if entry.updated_at else "",
    }


def _serialize_register(reg: StatutoryRegister, entries: Optional[List[RegisterEntry]] = None) -> dict:
    result = {
        "id": reg.id,
        "company_id": reg.company_id,
        "register_type": reg.register_type,
        "created_at": reg.created_at.isoformat() if reg.created_at else "",
        "updated_at": reg.updated_at.isoformat() if reg.updated_at else "",
        "entries": [],
    }
    if entries is not None:
        result["entries"] = [_serialize_entry(e) for e in entries]
    return result


def _next_entry_number(db: Session, register_id: int) -> int:
    """Get the next sequential entry number for a register."""
    max_num = (
        db.query(RegisterEntry.entry_number)
        .filter(RegisterEntry.register_id == register_id)
        .order_by(RegisterEntry.entry_number.desc())
        .first()
    )
    return (max_num[0] + 1) if max_num else 1


# ---------------------------------------------------------------------------
# Register type display names and Companies Act section references
# ---------------------------------------------------------------------------

REGISTER_DISPLAY_NAMES: Dict[str, str] = {
    "MEMBERS": "Register of Members (Section 88)",
    "DIRECTORS": "Register of Directors (Section 170)",
    "DIRECTORS_SHAREHOLDING": "Register of Directors' Shareholding (Section 170)",
    "CHARGES": "Register of Charges (Section 85)",
    "LOANS_GUARANTEES": "Register of Loans, Guarantees & Security (Section 186)",
    "INVESTMENTS": "Register of Investments (Section 186)",
    "RELATED_PARTY_CONTRACTS": "Register of Related Party Contracts (Section 189)",
    "SHARE_TRANSFERS": "Register of Share Transfers",
    "DEBENTURE_HOLDERS": "Register of Debenture Holders",
}


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("/summary")
def get_registers_summary(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("scale")),
):
    """Summary of all registers (entry counts, last updated)."""
    registers = _ensure_all_registers(db, company_id)
    items: List[dict] = []

    for reg in registers:
        entry_count = (
            db.query(RegisterEntry)
            .filter(RegisterEntry.register_id == reg.id)
            .count()
        )
        last_entry = (
            db.query(RegisterEntry)
            .filter(RegisterEntry.register_id == reg.id)
            .order_by(RegisterEntry.updated_at.desc())
            .first()
        )
        items.append({
            "register_type": reg.register_type,
            "register_id": reg.id,
            "entry_count": entry_count,
            "last_updated": last_entry.updated_at.isoformat() if last_entry and last_entry.updated_at else None,
        })

    return {"company_id": company_id, "registers": items}


@router.get("/")
def list_registers(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("scale")),
):
    """List all registers for company (auto-create if missing)."""
    registers = _ensure_all_registers(db, company_id)
    return [_serialize_register(r) for r in registers]


@router.get("/{register_type}")
def get_register(
    company_id: int,
    register_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("scale")),
):
    """Get register with all entries."""
    reg = _get_register(db, company_id, register_type)
    entries = (
        db.query(RegisterEntry)
        .filter(RegisterEntry.register_id == reg.id)
        .order_by(RegisterEntry.entry_number.asc())
        .all()
    )
    return _serialize_register(reg, entries)


@router.post("/{register_type}/entries", status_code=status.HTTP_201_CREATED)
def add_entry(
    company_id: int,
    register_type: str,
    body: RegisterEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("scale")),
):
    """Add entry to register."""
    reg = _get_register(db, company_id, register_type)

    try:
        entry_date = datetime.fromisoformat(body.entry_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid entry_date format. Use ISO format.")

    entry = RegisterEntry(
        register_id=reg.id,
        company_id=company_id,
        entry_number=_next_entry_number(db, reg.id),
        entry_date=entry_date,
        data=body.data,
        notes=body.notes,
        created_by=current_user.id,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return _serialize_entry(entry)


@router.put("/{register_type}/entries/{entry_id}")
def update_entry(
    company_id: int,
    register_type: str,
    entry_id: int,
    body: RegisterEntryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("scale")),
):
    """Update entry in register."""
    reg = _get_register(db, company_id, register_type)
    entry = (
        db.query(RegisterEntry)
        .filter(
            RegisterEntry.id == entry_id,
            RegisterEntry.register_id == reg.id,
        )
        .first()
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    if body.entry_date is not None:
        try:
            entry.entry_date = datetime.fromisoformat(body.entry_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid entry_date format.")
    if body.data is not None:
        entry.data = body.data
    if body.notes is not None:
        entry.notes = body.notes

    db.commit()
    db.refresh(entry)
    return _serialize_entry(entry)


@router.get("/{register_type}/export")
def export_register(
    company_id: int,
    register_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    _tier=Depends(require_tier("scale")),
):
    """Export register as formatted HTML (printable)."""
    reg = _get_register(db, company_id, register_type)
    entries = (
        db.query(RegisterEntry)
        .filter(RegisterEntry.register_id == reg.id)
        .order_by(RegisterEntry.entry_number.asc())
        .all()
    )

    rtype = register_type.upper()
    display_name = REGISTER_DISPLAY_NAMES.get(rtype, rtype)
    fields = REGISTER_DATA_FIELDS.get(rtype, [])

    # Build header columns
    header_cells = "".join(
        f"<th style='border:1px solid #333;padding:8px;background:#e9ecef;'>{f.replace('_', ' ').title()}</th>"
        for f in ["entry_no", "entry_date"] + fields + ["notes"]
    )

    # Build data rows
    rows_html = ""
    for entry in entries:
        cells = f"<td style='border:1px solid #ccc;padding:6px;text-align:center;'>{entry.entry_number}</td>"
        cells += f"<td style='border:1px solid #ccc;padding:6px;'>{entry.entry_date.strftime('%d-%m-%Y') if entry.entry_date else ''}</td>"
        data = entry.data or {}
        for f in fields:
            val = data.get(f, "")
            cells += f"<td style='border:1px solid #ccc;padding:6px;'>{val}</td>"
        cells += f"<td style='border:1px solid #ccc;padding:6px;'>{entry.notes or ''}</td>"
        rows_html += f"<tr>{cells}</tr>"

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{display_name} - Company #{company_id}</title>
    <style>
        body {{ font-family: 'Times New Roman', serif; margin: 40px; }}
        h1 {{ text-align: center; font-size: 18pt; margin-bottom: 5px; }}
        h2 {{ text-align: center; font-size: 14pt; color: #555; margin-top: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 10pt; }}
        .footer {{ margin-top: 40px; font-size: 9pt; color: #666; text-align: center; }}
        @media print {{
            body {{ margin: 20px; }}
            .no-print {{ display: none; }}
        }}
    </style>
</head>
<body>
    <h1>{display_name}</h1>
    <h2>Company ID: {company_id}</h2>
    <p style="text-align:center;color:#777;">Maintained under the Companies Act, 2013</p>

    <table>
        <thead><tr>{header_cells}</tr></thead>
        <tbody>{rows_html if rows_html else '<tr><td colspan="100%" style="text-align:center;padding:20px;color:#999;">No entries recorded</td></tr>'}</tbody>
    </table>

    <div class="footer">
        <p>Generated on {datetime.now(timezone.utc).strftime('%d %B %Y at %H:%M UTC')}</p>
        <p>This register is maintained as required under the Companies Act, 2013</p>
    </div>
</body>
</html>"""

    return Response(
        content=html,
        media_type="text/html",
        headers={"Content-Disposition": f'inline; filename="{rtype}_register_{company_id}.html"'},
    )
