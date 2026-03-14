"""Tests for the legal document template system endpoints."""


# ---------------------------------------------------------------------------
# Public template endpoints (no auth)
# ---------------------------------------------------------------------------


def test_list_templates_returns_28(client):
    """GET /api/v1/legal-docs/templates returns a list of 28 templates."""
    response = client.get("/api/v1/legal-docs/templates")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 28


def test_list_templates_contains_required_keys(client):
    """Each template in the list has template_type, name, and category."""
    response = client.get("/api/v1/legal-docs/templates")
    data = response.json()
    for tpl in data:
        assert "template_type" in tpl
        assert "name" in tpl
        assert "category" in tpl


def test_get_template_definition_nda(client):
    """GET /api/v1/legal-docs/templates/nda returns full definition with clauses and steps."""
    response = client.get("/api/v1/legal-docs/templates/nda")
    assert response.status_code == 200
    data = response.json()
    assert data["template_type"] == "nda"
    assert "name" in data
    assert "steps" in data
    assert "clauses" in data
    assert isinstance(data["steps"], list)
    assert isinstance(data["clauses"], list)
    assert len(data["steps"]) > 0
    assert len(data["clauses"]) > 0


def test_get_template_definition_nonexistent_returns_404(client):
    """GET /api/v1/legal-docs/templates/nonexistent returns 404."""
    response = client.get("/api/v1/legal-docs/templates/nonexistent")
    assert response.status_code == 404


def test_get_template_definition_founder_agreement(client):
    """GET /api/v1/legal-docs/templates/founder_agreement returns valid definition."""
    response = client.get("/api/v1/legal-docs/templates/founder_agreement")
    assert response.status_code == 200
    data = response.json()
    assert data["template_type"] == "founder_agreement"
    assert "steps" in data
    assert "clauses" in data


# ---------------------------------------------------------------------------
# Draft endpoints (auth required)
# ---------------------------------------------------------------------------


def test_create_draft_requires_auth(client):
    """POST /api/v1/legal-docs/drafts without auth returns 401."""
    response = client.post(
        "/api/v1/legal-docs/drafts",
        json={"template_type": "nda"},
    )
    assert response.status_code == 401


def test_create_draft_success(client, test_user, auth_headers):
    """POST /api/v1/legal-docs/drafts creates a draft document."""
    response = client.post(
        "/api/v1/legal-docs/drafts",
        json={"template_type": "nda", "title": "My NDA"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["template_type"] == "nda"
    assert data["title"] == "My NDA"
    assert data["status"] == "draft"


def test_create_draft_invalid_template_returns_400(client, test_user, auth_headers):
    """POST /api/v1/legal-docs/drafts with invalid template type returns 400."""
    response = client.post(
        "/api/v1/legal-docs/drafts",
        json={"template_type": "nonexistent_template"},
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_list_drafts_requires_auth(client):
    """GET /api/v1/legal-docs/drafts without auth returns 401."""
    response = client.get("/api/v1/legal-docs/drafts")
    assert response.status_code == 401


def test_list_drafts_returns_user_documents(client, test_user, auth_headers):
    """GET /api/v1/legal-docs/drafts lists only the current user's documents."""
    # Create two drafts
    client.post(
        "/api/v1/legal-docs/drafts",
        json={"template_type": "nda", "title": "Draft 1"},
        headers=auth_headers,
    )
    client.post(
        "/api/v1/legal-docs/drafts",
        json={"template_type": "nda", "title": "Draft 2"},
        headers=auth_headers,
    )

    response = client.get("/api/v1/legal-docs/drafts", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2


def test_update_clauses(client, test_user, auth_headers):
    """PUT /api/v1/legal-docs/drafts/{id}/clauses updates clause configuration."""
    # Create a draft first
    create_resp = client.post(
        "/api/v1/legal-docs/drafts",
        json={"template_type": "nda"},
        headers=auth_headers,
    )
    draft_id = create_resp.json()["id"]

    # Update clauses
    clauses_config = {"nda_type": "mutual", "governing_law": "Karnataka"}
    response = client.put(
        f"/api/v1/legal-docs/drafts/{draft_id}/clauses",
        json={"clauses_config": clauses_config},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["clauses_config"] == clauses_config
    assert data["status"] == "in_progress"


def test_generate_preview(client, test_user, auth_headers):
    """POST /api/v1/legal-docs/drafts/{id}/preview generates HTML preview."""
    create_resp = client.post(
        "/api/v1/legal-docs/drafts",
        json={"template_type": "nda"},
        headers=auth_headers,
    )
    draft_id = create_resp.json()["id"]

    response = client.post(
        f"/api/v1/legal-docs/drafts/{draft_id}/preview",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "generated_html" in data
    assert len(data["generated_html"]) > 0


def test_finalize_draft_without_preview_returns_400(client, test_user, auth_headers):
    """POST /api/v1/legal-docs/drafts/{id}/finalize without preview returns 400."""
    create_resp = client.post(
        "/api/v1/legal-docs/drafts",
        json={"template_type": "nda"},
        headers=auth_headers,
    )
    draft_id = create_resp.json()["id"]

    response = client.post(
        f"/api/v1/legal-docs/drafts/{draft_id}/finalize",
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_finalize_draft_after_preview(client, test_user, auth_headers):
    """POST /api/v1/legal-docs/drafts/{id}/finalize after preview succeeds."""
    create_resp = client.post(
        "/api/v1/legal-docs/drafts",
        json={"template_type": "nda"},
        headers=auth_headers,
    )
    draft_id = create_resp.json()["id"]

    # Generate preview first
    client.post(
        f"/api/v1/legal-docs/drafts/{draft_id}/preview",
        headers=auth_headers,
    )

    # Finalize
    response = client.post(
        f"/api/v1/legal-docs/drafts/{draft_id}/finalize",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "finalized"


def test_download_draft_without_html_returns_400(client, test_user, auth_headers):
    """GET /api/v1/legal-docs/drafts/{id}/download without generated HTML returns 400."""
    create_resp = client.post(
        "/api/v1/legal-docs/drafts",
        json={"template_type": "nda"},
        headers=auth_headers,
    )
    draft_id = create_resp.json()["id"]

    response = client.get(
        f"/api/v1/legal-docs/drafts/{draft_id}/download",
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_download_draft_returns_html(client, test_user, auth_headers):
    """GET /api/v1/legal-docs/drafts/{id}/download returns HTML content after preview."""
    create_resp = client.post(
        "/api/v1/legal-docs/drafts",
        json={"template_type": "nda"},
        headers=auth_headers,
    )
    draft_id = create_resp.json()["id"]

    # Generate preview first
    client.post(
        f"/api/v1/legal-docs/drafts/{draft_id}/preview",
        headers=auth_headers,
    )

    response = client.get(
        f"/api/v1/legal-docs/drafts/{draft_id}/download",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert "Content-Disposition" in response.headers


def test_get_nonexistent_draft_returns_404(client, test_user, auth_headers):
    """GET /api/v1/legal-docs/drafts/99999 returns 404."""
    response = client.get(
        "/api/v1/legal-docs/drafts/99999",
        headers=auth_headers,
    )
    assert response.status_code == 404
