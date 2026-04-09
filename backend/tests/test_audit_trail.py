"""Tests for the audit trail endpoints (company-level and document-level)."""


# ---------------------------------------------------------------------------
# GET /companies/{id}/audit-trail
# ---------------------------------------------------------------------------


def test_get_company_audit_trail_empty(
    client, test_user, auth_headers, test_company
):
    """GET /api/v1/companies/{id}/audit-trail returns empty entries initially."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/audit-trail",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["company_id"] == test_company.id
    assert data["total"] == 0
    assert data["entries"] == []


def test_get_company_audit_trail_requires_auth(client, test_company):
    """GET /api/v1/companies/{id}/audit-trail without auth returns 401."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/audit-trail",
    )
    assert response.status_code == 401


def test_get_company_audit_trail_wrong_company_returns_404(
    client, test_user, auth_headers
):
    """Audit trail for a non-owned company returns 404."""
    response = client.get(
        "/api/v1/companies/99999/audit-trail",
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_get_company_audit_trail_filter_by_entity_type(
    client, test_user, auth_headers, test_company
):
    """GET /api/v1/companies/{id}/audit-trail?entity_type=document returns filtered results."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/audit-trail?entity_type=document",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["company_id"] == test_company.id
    assert isinstance(data["entries"], list)


def test_get_company_audit_trail_filter_by_legal_document_type(
    client, test_user, auth_headers, test_company
):
    """Filtering by entity_type=legal_document returns only legal document entries."""
    # Create a draft with company_id and update clauses (which creates an audit entry)
    create_resp = client.post(
        "/api/v1/legal-docs/drafts",
        json={"template_type": "nda", "title": "Audited NDA", "company_id": test_company.id},
        headers=auth_headers,
    )
    draft_id = create_resp.json()["id"]

    # Update clauses to create an audit entry
    client.put(
        f"/api/v1/legal-docs/drafts/{draft_id}/clauses",
        json={"clauses_config": {"nda_type": "mutual"}},
        headers=auth_headers,
    )

    response = client.get(
        f"/api/v1/companies/{test_company.id}/audit-trail?entity_type=legal_document",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["entries"], list)
    # All returned entries should be of entity_type legal_document
    for entry in data["entries"]:
        assert entry["entity_type"] == "legal_document"


# ---------------------------------------------------------------------------
# GET /legal-docs/drafts/{id}/audit-trail — Document Audit Trail
# ---------------------------------------------------------------------------


def test_get_document_audit_trail_empty(
    client, test_user, auth_headers
):
    """GET /api/v1/legal-docs/drafts/{id}/audit-trail returns empty for new draft."""
    create_resp = client.post(
        "/api/v1/legal-docs/drafts",
        json={"template_type": "nda", "title": "Audit Test NDA"},
        headers=auth_headers,
    )
    draft_id = create_resp.json()["id"]

    response = client.get(
        f"/api/v1/legal-docs/drafts/{draft_id}/audit-trail",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["document_id"] == draft_id
    assert data["title"] == "Audit Test NDA"
    assert isinstance(data["entries"], list)
    assert len(data["entries"]) == 0


def test_get_document_audit_trail_requires_auth(
    client, test_user, auth_headers
):
    """GET /api/v1/legal-docs/drafts/{id}/audit-trail without auth returns 401."""
    create_resp = client.post(
        "/api/v1/legal-docs/drafts",
        json={"template_type": "nda"},
        headers=auth_headers,
    )
    draft_id = create_resp.json()["id"]

    response = client.get(
        f"/api/v1/legal-docs/drafts/{draft_id}/audit-trail",
    )
    assert response.status_code == 401


def test_get_document_audit_trail_nonexistent_returns_404(
    client, test_user, auth_headers
):
    """GET /api/v1/legal-docs/drafts/99999/audit-trail returns 404."""
    response = client.get(
        "/api/v1/legal-docs/drafts/99999/audit-trail",
        headers=auth_headers,
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Updating clauses creates audit entry
# ---------------------------------------------------------------------------


def test_update_clauses_creates_audit_entry(
    client, test_user, auth_headers
):
    """Updating clauses on a draft creates an audit trail entry."""
    create_resp = client.post(
        "/api/v1/legal-docs/drafts",
        json={"template_type": "nda", "title": "Clause Audit NDA"},
        headers=auth_headers,
    )
    draft_id = create_resp.json()["id"]

    # Update clauses
    client.put(
        f"/api/v1/legal-docs/drafts/{draft_id}/clauses",
        json={"clauses_config": {"nda_type": "mutual", "governing_law": "Karnataka"}},
        headers=auth_headers,
    )

    # Check audit trail
    response = client.get(
        f"/api/v1/legal-docs/drafts/{draft_id}/audit-trail",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["entries"]) >= 1

    # Find the update entry
    update_entries = [e for e in data["entries"] if e["action"] == "update"]
    assert len(update_entries) >= 1
    assert "clauses_config" in update_entries[0]["changes"]


def test_multiple_clause_updates_create_multiple_entries(
    client, test_user, auth_headers
):
    """Multiple clause updates create multiple audit entries."""
    create_resp = client.post(
        "/api/v1/legal-docs/drafts",
        json={"template_type": "nda", "title": "Multi Update NDA"},
        headers=auth_headers,
    )
    draft_id = create_resp.json()["id"]

    # First update
    client.put(
        f"/api/v1/legal-docs/drafts/{draft_id}/clauses",
        json={"clauses_config": {"nda_type": "mutual"}},
        headers=auth_headers,
    )
    # Second update
    client.put(
        f"/api/v1/legal-docs/drafts/{draft_id}/clauses",
        json={"clauses_config": {"nda_type": "unilateral", "governing_law": "Delhi"}},
        headers=auth_headers,
    )

    response = client.get(
        f"/api/v1/legal-docs/drafts/{draft_id}/audit-trail",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    update_entries = [e for e in data["entries"] if e["action"] == "update"]
    assert len(update_entries) >= 2


# ---------------------------------------------------------------------------
# Finalizing creates audit entry
# ---------------------------------------------------------------------------


def test_finalize_creates_audit_entry(
    client, test_user, auth_headers
):
    """Finalizing a document creates a 'finalize' audit trail entry."""
    create_resp = client.post(
        "/api/v1/legal-docs/drafts",
        json={"template_type": "nda", "title": "Finalize Audit NDA"},
        headers=auth_headers,
    )
    draft_id = create_resp.json()["id"]

    # Generate preview (required before finalize)
    client.post(
        f"/api/v1/legal-docs/drafts/{draft_id}/preview",
        headers=auth_headers,
    )

    # Finalize
    finalize_resp = client.post(
        f"/api/v1/legal-docs/drafts/{draft_id}/finalize",
        headers=auth_headers,
    )
    assert finalize_resp.status_code == 200
    assert finalize_resp.json()["status"] == "finalized"

    # Check audit trail
    response = client.get(
        f"/api/v1/legal-docs/drafts/{draft_id}/audit-trail",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    finalize_entries = [e for e in data["entries"] if e["action"] == "finalize"]
    assert len(finalize_entries) >= 1
    # Should track the status change
    assert "status" in finalize_entries[0]["changes"]
    assert finalize_entries[0]["changes"]["status"]["new"] == "finalized"


# ---------------------------------------------------------------------------
# POST /legal-docs/drafts/{id}/revise — Revision creates audit entries
# ---------------------------------------------------------------------------


def test_revise_creates_audit_entry(
    client, test_user, auth_headers
):
    """Revising a finalized document creates audit trail entries."""
    # Create, preview, and finalize a document
    create_resp = client.post(
        "/api/v1/legal-docs/drafts",
        json={"template_type": "nda", "title": "Revise Audit NDA"},
        headers=auth_headers,
    )
    draft_id = create_resp.json()["id"]

    client.post(
        f"/api/v1/legal-docs/drafts/{draft_id}/preview",
        headers=auth_headers,
    )
    client.post(
        f"/api/v1/legal-docs/drafts/{draft_id}/finalize",
        headers=auth_headers,
    )

    # Revise
    revise_resp = client.post(
        f"/api/v1/legal-docs/drafts/{draft_id}/revise",
        json={"reason": "Need to update terms"},
        headers=auth_headers,
    )
    assert revise_resp.status_code == 201
    revision = revise_resp.json()
    assert revision["version"] == 2
    assert revision["status"] == "draft"

    # Check audit trail on the original document
    response = client.get(
        f"/api/v1/legal-docs/drafts/{draft_id}/audit-trail",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    revise_entries = [e for e in data["entries"] if e["action"] == "revise"]
    assert len(revise_entries) >= 1


def test_revise_only_finalized_docs(
    client, test_user, auth_headers
):
    """POST /api/v1/legal-docs/drafts/{id}/revise on a draft returns 400."""
    create_resp = client.post(
        "/api/v1/legal-docs/drafts",
        json={"template_type": "nda", "title": "Draft Only NDA"},
        headers=auth_headers,
    )
    draft_id = create_resp.json()["id"]

    response = client.post(
        f"/api/v1/legal-docs/drafts/{draft_id}/revise",
        headers=auth_headers,
    )
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# GET /legal-docs/drafts/{id}/versions — Version Chain
# ---------------------------------------------------------------------------


def test_get_document_versions_single(
    client, test_user, auth_headers
):
    """GET /api/v1/legal-docs/drafts/{id}/versions returns single version for a new doc."""
    create_resp = client.post(
        "/api/v1/legal-docs/drafts",
        json={"template_type": "nda", "title": "Version Test NDA"},
        headers=auth_headers,
    )
    draft_id = create_resp.json()["id"]

    response = client.get(
        f"/api/v1/legal-docs/drafts/{draft_id}/versions",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["current_id"] == draft_id
    assert isinstance(data["versions"], list)
    assert len(data["versions"]) >= 1
    # The current doc should be marked
    current_versions = [v for v in data["versions"] if v["is_current"]]
    assert len(current_versions) == 1


def test_get_document_versions_after_revise(
    client, test_user, auth_headers
):
    """After revising, the versions endpoint shows the full chain."""
    # Create, preview, finalize
    create_resp = client.post(
        "/api/v1/legal-docs/drafts",
        json={"template_type": "nda", "title": "Version Chain NDA"},
        headers=auth_headers,
    )
    original_id = create_resp.json()["id"]

    client.post(
        f"/api/v1/legal-docs/drafts/{original_id}/preview",
        headers=auth_headers,
    )
    client.post(
        f"/api/v1/legal-docs/drafts/{original_id}/finalize",
        headers=auth_headers,
    )

    # Revise
    revise_resp = client.post(
        f"/api/v1/legal-docs/drafts/{original_id}/revise",
        json={"reason": "Add new terms"},
        headers=auth_headers,
    )
    revision_id = revise_resp.json()["id"]

    # Check versions from the revision
    response = client.get(
        f"/api/v1/legal-docs/drafts/{revision_id}/versions",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["current_id"] == revision_id
    assert len(data["versions"]) >= 2

    # Versions should include both the original and the revision
    version_ids = [v["id"] for v in data["versions"]]
    assert original_id in version_ids
    assert revision_id in version_ids


def test_get_document_versions_requires_auth(
    client, test_user, auth_headers
):
    """GET /api/v1/legal-docs/drafts/{id}/versions without auth returns 401."""
    create_resp = client.post(
        "/api/v1/legal-docs/drafts",
        json={"template_type": "nda"},
        headers=auth_headers,
    )
    draft_id = create_resp.json()["id"]

    response = client.get(
        f"/api/v1/legal-docs/drafts/{draft_id}/versions",
    )
    assert response.status_code == 401


def test_get_document_versions_nonexistent_returns_404(
    client, test_user, auth_headers
):
    """GET /api/v1/legal-docs/drafts/99999/versions returns 404."""
    response = client.get(
        "/api/v1/legal-docs/drafts/99999/versions",
        headers=auth_headers,
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Audit trail tracks changes with old/new values
# ---------------------------------------------------------------------------


def test_audit_entry_tracks_old_and_new_values(
    client, test_user, auth_headers
):
    """Audit entries for clause updates track old and new clause config values."""
    create_resp = client.post(
        "/api/v1/legal-docs/drafts",
        json={"template_type": "nda", "title": "Old/New Audit NDA"},
        headers=auth_headers,
    )
    draft_id = create_resp.json()["id"]

    # First update (old is empty/default)
    client.put(
        f"/api/v1/legal-docs/drafts/{draft_id}/clauses",
        json={"clauses_config": {"nda_type": "mutual"}},
        headers=auth_headers,
    )

    # Second update
    client.put(
        f"/api/v1/legal-docs/drafts/{draft_id}/clauses",
        json={"clauses_config": {"nda_type": "unilateral"}},
        headers=auth_headers,
    )

    response = client.get(
        f"/api/v1/legal-docs/drafts/{draft_id}/audit-trail",
        headers=auth_headers,
    )
    data = response.json()
    # The most recent entry (first in list, ordered by desc) should show the change
    update_entries = [e for e in data["entries"] if e["action"] == "update"]
    assert len(update_entries) >= 2

    # Check that the latest update entry has both old and new
    latest = update_entries[0]
    assert "clauses_config" in latest["changes"]
    changes = latest["changes"]["clauses_config"]
    assert "old" in changes
    assert "new" in changes
    assert changes["new"]["nda_type"] == "unilateral"
    assert changes["old"]["nda_type"] == "mutual"


# ---------------------------------------------------------------------------
# Audit trail for finalized document with company_id
# ---------------------------------------------------------------------------


def test_company_audit_trail_populated_after_doc_operations(
    client, test_user, auth_headers, test_company
):
    """Company audit trail is populated after document operations with company_id."""
    # Create a draft linked to the company
    create_resp = client.post(
        "/api/v1/legal-docs/drafts",
        json={
            "template_type": "nda",
            "title": "Company Linked NDA",
            "company_id": test_company.id,
        },
        headers=auth_headers,
    )
    draft_id = create_resp.json()["id"]

    # Update clauses
    client.put(
        f"/api/v1/legal-docs/drafts/{draft_id}/clauses",
        json={"clauses_config": {"nda_type": "mutual"}},
        headers=auth_headers,
    )

    # Preview and finalize
    client.post(
        f"/api/v1/legal-docs/drafts/{draft_id}/preview",
        headers=auth_headers,
    )
    client.post(
        f"/api/v1/legal-docs/drafts/{draft_id}/finalize",
        headers=auth_headers,
    )

    # Company audit trail should now have entries
    response = client.get(
        f"/api/v1/companies/{test_company.id}/audit-trail",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 2  # At least update and finalize
    actions = [e["action"] for e in data["entries"]]
    assert "update" in actions
    assert "finalize" in actions
