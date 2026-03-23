# Workflow Gaps & Fixes — Source of Truth

> Last updated: 2026-03-23
> Status: Active implementation

## Executive Summary

Every major founder workflow suffers from the same 5 architectural problems:

1. **Checklist state lives in localStorage only** — not persisted to backend
2. **Documents generated but orphaned** — `createLegalDraft()` creates documents never linked to the workflow
3. **"Send for Signing" buttons are stubs** — set a frontend flag, no actual e-sign API call
4. **Compliance filings are manual checkboxes** — no form generation, no ROC submission, no deadlines
5. **Entity type doesn't affect any workflow** — OPC, LLP, Section 8 see identical flows to Pvt Ltd

---

## Fix Strategy

### Phase 1: Backend Foundation
Add workflow state fields to existing models so frontend can persist checklist state.

**FundingRound model** — add JSON column `checklist_state` for the 7-step checklist.
**ESOPPlan model** — add JSON column `approval_state` for the 5-step approval wizard.
**Meeting model** — add columns for resolution votes (JSON), minutes signature request ID, notice document ID.
**New model: ShareIssuanceWorkflow** — tracks the 8-step share issuance process per company.

### Phase 2: Workflow Fixes (parallelizable per workflow)

#### 2A — Share Issuance
- Backend: Create ShareIssuanceWorkflow model + CRUD endpoints
- Backend: Save/load wizard state, validate each step
- Frontend: Replace useState with API persistence, call linkDocument after draft creation
- Frontend: Replace "Send for Signing" stub with createSignatureRequest + sendSigningEmails
- Backend: Add entity type validation (block multiple shareholders for OPC, block for LLP)
- Backend: Validate authorized capital server-side before allotment

#### 2B — Fundraising
- Frontend: Call `linkRoundDocument()` after every `createLegalDraft()` call
- Backend: Add `checklist_state` JSON column to FundingRound + save/load endpoints
- Frontend: Add "foreign" to investor_type dropdown options
- Backend: Fix closing room — documents now properly linked, e-sign requests will actually send
- Frontend: Persist funds_received to backend (update RoundInvestor.funds_received via API)
- Backend: Validate price_per_share is set before allotment (no 10.0 fallback)

#### 2C — ESOP
- Backend: Add `approval_state` JSON column to ESOPPlan + save/load endpoints
- Backend: Validate board_resolution_document_id + shareholder_resolution_document_id before activation
- Frontend: After createLegalDraft, call API to set board_resolution_document_id / shareholder_resolution_document_id
- Frontend: After createSignatureRequest, call API to track signature request ID
- Backend: Add webhook/polling to auto-update grant status to ACCEPTED when employee signs

#### 2D — Meetings & Resolutions
- Backend: Add `resolution_votes` JSON column to Meeting (per-attendee vote detail)
- Backend: Add `notice_document_id` FK to LegalDocument, `minutes_signature_request_id` FK to SignatureRequest
- Frontend: Save votes to backend via updateMeetingResolutions (include vote detail, not just results)
- Frontend: Replace minutes signing text field with e-sign: createSignatureRequest for chairman
- Frontend: Replace "Send for Signing" stub in ResolutionWorkflow with real createSignatureRequest call
- Backend: Auto-populate board resolution document with meeting resolution data
- Frontend: Persist filing status changes to backend

### Phase 3: Entity Type Guards
- Backend: Add `entity_types` list to each template definition in contract_template_service
- Backend: Filter templates by company entity_type in get_available_templates()
- Frontend: Hide share-based workflows for LLP (show capital contribution view)
- Frontend: Block multiple shareholders for OPC in cap table
- Backend: Block ESOP for sole_proprietorship, partnership
- Backend: Skip board meeting requirements for OPC/LLP in compliance engine
- Frontend: Show entity-appropriate labels (partner vs director, contribution vs shares)

### Phase 4: Document Generation
- Backend: Generate PAS-3, MGT-14, SH-7, SH-4 as HTML documents (not just JSON)
- Backend: Add missing templates (EGM notice with agenda, Special Resolution, Transfer Deed, PAS-4 per-allottee)
- Backend: Connect share certificate to e-sign (add director/CS signature fields)
- Backend: Store workflow-generated MOA/AOA as LegalDocument records (not just JSON dicts)

### Phase 5: Auto-Population & Integration
- Backend: Auto-create Register of Members entries when cap table changes
- Backend: Auto-create Register of Share Transfers entries on record_transfer()
- Backend: Link latest valuation to ESOP exercise price and fundraising
- Backend: Store signed documents in data room after e-sign completion
- Backend: Auto-create compliance tasks when company reaches INCORPORATED status

---

## Detailed Gap Inventory

### Share Issuance Wizard

| Step | Gap | Fix |
|------|-----|-----|
| All | State in useState only, no persistence | Create ShareIssuanceWorkflow model, save/load API |
| 1. Pre-Check | No authorized capital validation server-side | Add validation in allotment endpoint |
| 1. Pre-Check | No OPC single-shareholder guard | Check entity_type, block if OPC + existing shareholder |
| 1. Pre-Check | No LLP flow variant | Show capital contribution UI for LLP |
| 2. Board Resolution | Draft not linked to workflow | After createLegalDraft, save document_id to workflow state |
| 2. Board Resolution | "Send for Signing" is stub | Replace with createSignatureRequest + sendSigningEmails |
| 3. Shareholder Approval | No voting mechanism | Use e-sign with multiple signatories for SR |
| 3. Shareholder Approval | 200-person limit not checked (Section 42) | Backend validation |
| 4. Regulatory Filing | No form generation | Generate MGT-14, SH-7 as HTML documents |
| 4. Regulatory Filing | No deadline tracking | Create ComplianceTask records |
| 5. Offer Letters | Single template, not per-allottee | Generate individual PAS-4 per allottee |
| 5. Offer Letters | No email sending | Send via e-sign system or email service |
| 6. Receive Funds | No bank reconciliation | Track fund receipt dates in backend |
| 7. Allotment | No validation board resolution was signed | Check signature request status before allowing |
| 8. Post-Allotment | Certificates have no signatures | Connect to e-sign for director/CS |
| 8. Post-Allotment | PAS-3 filed is checkbox only | Generate PAS-3 document, track filing |

### Fundraising

| Step | Gap | Fix |
|------|-----|-----|
| All | Checklist in localStorage only | Add checklist_state JSON to FundingRound |
| 2. SHA/SSA | linkRoundDocument() never called | Call after createLegalDraft |
| 3. Board | Resolution not linked to round | Save document_id to checklist_state |
| 4. SR | No voting validation | Track shareholder approval properly |
| 5. Filings | No form generation | Generate MGT-14, SH-7 documents |
| 6. Allotment | price_per_share fallback to 10.0 | Validate > 0 before allotment |
| 6. Allotment | funds_received not sent to backend | Update RoundInvestor.funds_received via API |
| 7. Post-Close | No PAS-3/certificate generation | Generate and track |
| Closing Room | Documents never linked = e-signs never sent | Fix linkRoundDocument call |
| Foreign | No "foreign" investor type option | Add to dropdown + FC-GPR logic |

### ESOP

| Step | Gap | Fix |
|------|-----|-----|
| All | Approval state in localStorage | Add approval_state JSON to ESOPPlan |
| 2. Board | board_resolution_document_id never set | Set after createLegalDraft |
| 3. SR | shareholder_resolution_document_id never set | Set after createLegalDraft |
| 4. MGT-14 | No form generation | Generate MGT-14 document |
| 5. Activation | No validation steps 1-4 complete | Check document IDs + signature status |
| Grants | accepted_at never set | Webhook/poll to update on employee sign |
| Exercise | No PAS-3 form generated | Generate PAS-3 on exercise |
| Entity | Available for all entity types | Block for sole_prop, partnership |

### Meetings & Resolutions

| Feature | Gap | Fix |
|---------|-----|-----|
| Votes | Individual votes in localStorage only | Add resolution_votes JSON to Meeting |
| Minutes | Signing is text field, not e-sign | Create SignatureRequest for chairman |
| Notice | Generated HTML not stored as LegalDocument | Save to LegalDocument, enable e-sign |
| Resolution Doc | createLegalDraft creates empty draft | Populate with resolution text, votes, attendees |
| Send for Signing | Stub (just displays message) | Real createSignatureRequest call |
| Filing Status | localStorage only | Add meeting filing endpoint |
| AGM/EGM | Identical to board meeting | Add proxy voting, shareholder distinction |
| Quorum | Boolean flag, no enforcement | Calculate 1/3 directors or 2, validate |
| Entity Type | No guards | Hide for OPC/LLP, show for Pvt Ltd/Section 8 |

### Document Templates → E-Sign Chain

| Gap | Fix |
|-----|-----|
| Templates not filtered by entity type | Add entity_types field, filter in API |
| MOA/AOA generated as JSON dict, not LegalDocument | Store in LegalDocument table |
| Meeting notice not stored as LegalDocument | Save to LegalDocument after generation |
| Signed documents not stored in data room | Auto-create Document record after completion |
| No version history for clause changes | Add version tracking to LegalDocument |

### Entity Type Workflow Variations

| Entity | Cap Table | ESOP | Board Meetings | Fundraising | Documents |
|--------|-----------|------|----------------|-------------|-----------|
| Pvt Ltd | Full (shares) | Yes | 4/year required | Full | MOA + AOA |
| OPC | Single shareholder only | No (typically) | Not required | Limited | MOA + AOA + INC-3 |
| LLP | Capital contributions (not shares) | No | Not required | No equity raising | LLP Agreement |
| Section 8 | Shares (no dividends) | No | 4/year required | No | MOA + AOA (charitable) |
| Partnership | Partner interests | No | Not required | No | Partnership Deed |
| Sole Prop | 100% owner | No | N/A | No | Declaration |
| Public Ltd | Full (unrestricted transfer) | Yes | 4/year + committees | Full | MOA + AOA + Prospectus |
