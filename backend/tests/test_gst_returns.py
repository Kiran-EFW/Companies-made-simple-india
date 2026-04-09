"""Tests for GST return endpoints under /companies/{id}/compliance/gst/."""


# ---------------------------------------------------------------------------
# GSTIN Validation
# ---------------------------------------------------------------------------


def test_validate_gstin_valid(client, test_user, auth_headers, test_company):
    """POST validate-gstin with a valid GSTIN returns valid=True and state info."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/compliance/gst/validate-gstin",
        json={"gstin": "27AAPFU0939F1ZV"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert "state_code" in data
    assert data["state_code"] == "27"


def test_validate_gstin_too_short(client, test_user, auth_headers, test_company):
    """POST validate-gstin with a short GSTIN returns valid=False."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/compliance/gst/validate-gstin",
        json={"gstin": "27AAPFU"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert "error" in data


def test_validate_gstin_invalid_format(client, test_user, auth_headers, test_company):
    """POST validate-gstin with invalid format (missing mandatory Z) returns valid=False."""
    # The GSTIN regex requires 'Z' at position 13; replacing it breaks the format
    response = client.post(
        f"/api/v1/companies/{test_company.id}/compliance/gst/validate-gstin",
        json={"gstin": "27AAPFU0939F1AV"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert "error" in data


def test_validate_gstin_requires_auth(client, test_company):
    """POST validate-gstin without auth returns 401."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/compliance/gst/validate-gstin",
        json={"gstin": "27AAPFU0939F1ZV"},
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# State Codes
# ---------------------------------------------------------------------------


def test_get_state_codes(client, test_user, auth_headers, test_company):
    """GET state-codes returns a dict of state codes."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/compliance/gst/state-codes",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "state_codes" in data
    assert isinstance(data["state_codes"], dict)
    # Maharashtra should be present (code 27)
    assert "27" in data["state_codes"]


def test_get_state_codes_requires_auth(client, test_company):
    """GET state-codes without auth returns 401."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/compliance/gst/state-codes",
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# GSTR-1 Generation
# ---------------------------------------------------------------------------


SAMPLE_INVOICE = {
    "invoice_number": "INV001",
    "invoice_date": "2025-04-01",
    "receiver_gstin": "29AAPFU0939F1ZV",
    "invoice_value": 10000,
    "taxable_value": 10000,
    "igst": 1800,
    "cgst": 0,
    "sgst": 0,
    "invoice_type": "B2B",
}


def test_generate_gstr1(client, test_user, auth_headers, test_company):
    """POST gstr1/generate with valid data returns GSTR-1 JSON."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/compliance/gst/gstr1/generate",
        json={
            "gstin": "27AAPFU0939F1ZV",
            "filing_period": "042025",
            "invoices": [SAMPLE_INVOICE],
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "gstr1" in data
    assert data["invoice_count"] == 1


def test_generate_gstr1_invalid_gstin_returns_400(
    client, test_user, auth_headers, test_company
):
    """POST gstr1/generate with invalid GSTIN returns 400."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/compliance/gst/gstr1/generate",
        json={
            "gstin": "INVALID",
            "filing_period": "042025",
            "invoices": [SAMPLE_INVOICE],
        },
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_generate_gstr1_requires_auth(client, test_company):
    """POST gstr1/generate without auth returns 401."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/compliance/gst/gstr1/generate",
        json={
            "gstin": "27AAPFU0939F1ZV",
            "filing_period": "042025",
            "invoices": [SAMPLE_INVOICE],
        },
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# GSTR-3B Generation
# ---------------------------------------------------------------------------


def test_generate_gstr3b(client, test_user, auth_headers, test_company):
    """POST gstr3b/generate with valid data returns GSTR-3B JSON."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/compliance/gst/gstr3b/generate",
        json={
            "gstin": "27AAPFU0939F1ZV",
            "filing_period": "042025",
            "outward_taxable": {
                "taxable_value": 100000,
                "igst": 18000,
                "cgst": 0,
                "sgst": 0,
            },
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "gstr3b" in data


def test_generate_gstr3b_invalid_gstin_returns_400(
    client, test_user, auth_headers, test_company
):
    """POST gstr3b/generate with invalid GSTIN returns 400."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/compliance/gst/gstr3b/generate",
        json={
            "gstin": "BAD",
            "filing_period": "042025",
            "outward_taxable": {
                "taxable_value": 100000,
                "igst": 18000,
                "cgst": 0,
                "sgst": 0,
            },
        },
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_generate_gstr3b_requires_auth(client, test_company):
    """POST gstr3b/generate without auth returns 401."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/compliance/gst/gstr3b/generate",
        json={
            "gstin": "27AAPFU0939F1ZV",
            "filing_period": "042025",
            "outward_taxable": {
                "taxable_value": 100000,
                "igst": 18000,
                "cgst": 0,
                "sgst": 0,
            },
        },
    )
    assert response.status_code == 401


def test_generate_gstr3b_wrong_company_returns_404(client, test_user, auth_headers):
    """GSTR-3B for a non-owned company returns 404."""
    response = client.post(
        "/api/v1/companies/99999/compliance/gst/gstr3b/generate",
        json={
            "gstin": "27AAPFU0939F1ZV",
            "filing_period": "042025",
        },
        headers=auth_headers,
    )
    assert response.status_code == 404
