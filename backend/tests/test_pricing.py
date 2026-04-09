"""Tests for pricing endpoints."""


def test_calculate_pricing(client):
    """Pricing calculation returns a valid breakdown."""
    response = client.post(
        "/api/v1/pricing/calculate",
        json={
            "entity_type": "private_limited",
            "plan_tier": "launch",
            "state": "delhi",
            "authorized_capital": 100000,
            "num_directors": 2,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["entity_type"] == "private_limited"
    assert data["plan_tier"] == "launch"
    assert data["platform_fee"] > 0  # actual amount depends on current pricing config
    assert "government_fees" in data
    assert "dsc" in data
    assert "grand_total" in data
    assert data["grand_total"] > 0


def test_pricing_different_state(client):
    """Pricing varies by state due to stamp duty differences."""
    resp_delhi = client.post(
        "/api/v1/pricing/calculate",
        json={
            "entity_type": "private_limited",
            "state": "delhi",
            "authorized_capital": 100000,
            "num_directors": 2,
        },
    )
    resp_punjab = client.post(
        "/api/v1/pricing/calculate",
        json={
            "entity_type": "private_limited",
            "state": "punjab",
            "authorized_capital": 100000,
            "num_directors": 2,
        },
    )
    delhi_total = resp_delhi.json()["grand_total"]
    punjab_total = resp_punjab.json()["grand_total"]
    # Punjab has much higher stamp duty than Delhi
    assert punjab_total > delhi_total


def test_list_states(client):
    """States endpoint returns a non-empty list of state options."""
    response = client.get("/api/v1/pricing/states")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 20  # We have 30+ states
    # Each state has value and label
    first = data[0]
    assert "value" in first
    assert "label" in first


def test_list_plans(client):
    """Plans endpoint returns platform fee plans."""
    response = client.get("/api/v1/pricing/plans")
    assert response.status_code == 200
    data = response.json()
    assert "private_limited" in data
    assert "opc" in data
    assert "llp" in data


def test_pricing_with_existing_dsc(client):
    """If user has existing DSC, DSC cost should be zero."""
    response = client.post(
        "/api/v1/pricing/calculate",
        json={
            "entity_type": "private_limited",
            "state": "delhi",
            "authorized_capital": 100000,
            "num_directors": 2,
            "has_existing_dsc": True,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["dsc"]["total_dsc"] == 0
