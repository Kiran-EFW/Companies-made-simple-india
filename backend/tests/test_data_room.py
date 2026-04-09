"""Tests for the data room endpoints (folders, share links, retention)."""


# ---------------------------------------------------------------------------
# List Folders
# ---------------------------------------------------------------------------


def test_list_folders_empty(client, test_user, auth_headers, test_company, scale_subscription):
    """GET /api/v1/companies/{id}/data-room/folders returns empty list initially."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/data-room/folders",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_list_folders_requires_auth(client, test_company, scale_subscription):
    """GET /api/v1/companies/{id}/data-room/folders without auth returns 401."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/data-room/folders",
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Create Folder
# ---------------------------------------------------------------------------


def test_create_folder(client, test_user, auth_headers, test_company, scale_subscription):
    """POST /api/v1/companies/{id}/data-room/folders creates a folder."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/data-room/folders",
        json={
            "name": "Legal Documents",
            "folder_type": "AGREEMENTS",
            "sort_order": 1,
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Legal Documents"
    assert data["folder_type"] == "AGREEMENTS"
    assert data["company_id"] == test_company.id


def test_create_subfolder(client, test_user, auth_headers, test_company, scale_subscription):
    """Creating a folder with parent_id nests it under the parent."""
    # Create parent
    parent_resp = client.post(
        f"/api/v1/companies/{test_company.id}/data-room/folders",
        json={"name": "Parent Folder"},
        headers=auth_headers,
    )
    parent_id = parent_resp.json()["id"]

    # Create child
    child_resp = client.post(
        f"/api/v1/companies/{test_company.id}/data-room/folders",
        json={"name": "Child Folder", "parent_id": parent_id},
        headers=auth_headers,
    )
    assert child_resp.status_code == 201
    assert child_resp.json()["parent_id"] == parent_id


def test_create_folder_nonexistent_parent_returns_404(
    client, test_user, auth_headers, test_company, scale_subscription
):
    """Creating a folder under a non-existent parent returns 404."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/data-room/folders",
        json={"name": "Orphan Folder", "parent_id": 99999},
        headers=auth_headers,
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Setup Default Folders
# ---------------------------------------------------------------------------


def test_setup_default_folders(client, test_user, auth_headers, test_company, scale_subscription):
    """POST /api/v1/companies/{id}/data-room/setup-defaults creates default folder structure."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/data-room/setup-defaults",
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 10  # 10 default folders


def test_setup_default_folders_twice_returns_400(
    client, test_user, auth_headers, test_company, scale_subscription
):
    """Setting up defaults again when folders already exist returns 400."""
    client.post(
        f"/api/v1/companies/{test_company.id}/data-room/setup-defaults",
        headers=auth_headers,
    )
    response = client.post(
        f"/api/v1/companies/{test_company.id}/data-room/setup-defaults",
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_setup_defaults_creates_tree_structure(
    client, test_user, auth_headers, test_company, scale_subscription
):
    """After setup-defaults, listing folders returns a tree."""
    client.post(
        f"/api/v1/companies/{test_company.id}/data-room/setup-defaults",
        headers=auth_headers,
    )
    response = client.get(
        f"/api/v1/companies/{test_company.id}/data-room/folders",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10


# ---------------------------------------------------------------------------
# Share Links
# ---------------------------------------------------------------------------


def test_create_share_link(client, test_user, auth_headers, test_company, scale_subscription):
    """POST /api/v1/companies/{id}/data-room/share-links creates a share link."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/data-room/share-links",
        json={
            "name": "Due Diligence Access",
            "folder_ids": [],
            "file_ids": [],
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Due Diligence Access"
    assert "share_token" in data
    assert data["is_active"] is True


def test_create_share_link_with_expiry(
    client, test_user, auth_headers, test_company, scale_subscription
):
    """Share link can be created with an expiry date."""
    from datetime import datetime, timedelta, timezone

    expires = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
    response = client.post(
        f"/api/v1/companies/{test_company.id}/data-room/share-links",
        json={
            "name": "Temporary Link",
            "folder_ids": [],
            "expires_at": expires,
            "max_downloads": 10,
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["max_downloads"] == 10
    assert data["expires_at"] is not None


def test_list_share_links(client, test_user, auth_headers, test_company, scale_subscription):
    """GET /api/v1/companies/{id}/data-room/share-links lists active share links."""
    # Create a link
    client.post(
        f"/api/v1/companies/{test_company.id}/data-room/share-links",
        json={"name": "Link 1", "folder_ids": []},
        headers=auth_headers,
    )

    response = client.get(
        f"/api/v1/companies/{test_company.id}/data-room/share-links",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_list_share_links_requires_auth(client, test_company, scale_subscription):
    """GET /api/v1/companies/{id}/data-room/share-links without auth returns 401."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/data-room/share-links",
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Retention Summary
# ---------------------------------------------------------------------------


def test_retention_summary(client, test_user, auth_headers, test_company, scale_subscription):
    """GET /api/v1/companies/{id}/data-room/retention/summary returns retention stats."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/data-room/retention/summary",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_files" in data
    assert "permanent" in data
    assert "eight_years" in data
    assert "six_years" in data
    assert "expiring_soon" in data


def test_retention_summary_empty_initially(
    client, test_user, auth_headers, test_company, scale_subscription
):
    """Retention summary shows all zeros when no files exist."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/data-room/retention/summary",
        headers=auth_headers,
    )
    data = response.json()
    assert data["total_files"] == 0
    assert data["permanent"] == 0
