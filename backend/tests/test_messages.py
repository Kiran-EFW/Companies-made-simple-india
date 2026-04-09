"""Tests for the messages router — two-way conversation between founders and admin."""


# ---------------------------------------------------------------------------
# Send Message
# ---------------------------------------------------------------------------


def test_send_message(client, test_user, auth_headers, test_company):
    """POST /companies/{id}/messages creates a message and returns it."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/messages",
        json={"content": "Hello from test"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["content"] == "Hello from test"
    assert data["sender_type"] == "founder"
    assert data["sender_id"] == test_user.id
    assert data["company_id"] == test_company.id
    assert data["is_read"] is False


def test_send_message_empty_content_returns_400(
    client, test_user, auth_headers, test_company
):
    """POST with empty content returns 400."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/messages",
        json={"content": "   "},
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_send_message_requires_auth(client, test_company):
    """POST /companies/{id}/messages without auth returns 401."""
    response = client.post(
        f"/api/v1/companies/{test_company.id}/messages",
        json={"content": "Hello"},
    )
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# List Messages
# ---------------------------------------------------------------------------


def test_list_messages_empty(client, test_user, auth_headers, test_company):
    """GET /companies/{id}/messages returns empty list initially."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/messages",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["company_id"] == test_company.id
    assert isinstance(data["messages"], list)
    assert data["total"] == 0


def test_list_messages_after_send(client, test_user, auth_headers, test_company):
    """GET returns the message after sending one."""
    client.post(
        f"/api/v1/companies/{test_company.id}/messages",
        json={"content": "Hello from test"},
        headers=auth_headers,
    )

    response = client.get(
        f"/api/v1/companies/{test_company.id}/messages",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    messages = data["messages"]
    assert any(m["content"] == "Hello from test" for m in messages)


def test_list_messages_requires_auth(client, test_company):
    """GET /companies/{id}/messages without auth returns 401."""
    response = client.get(
        f"/api/v1/companies/{test_company.id}/messages",
    )
    assert response.status_code == 401


def test_message_has_sender_info(client, test_user, auth_headers, test_company):
    """Messages include sender name and type."""
    client.post(
        f"/api/v1/companies/{test_company.id}/messages",
        json={"content": "Checking sender info"},
        headers=auth_headers,
    )

    response = client.get(
        f"/api/v1/companies/{test_company.id}/messages",
        headers=auth_headers,
    )
    assert response.status_code == 200
    msg = response.json()["messages"][0]
    assert msg["sender_name"] is not None
    assert msg["sender_name"] == test_user.full_name
    assert msg["sender_type"] == "founder"
    assert msg["sender_id"] == test_user.id


# ---------------------------------------------------------------------------
# Mark Messages Read
# ---------------------------------------------------------------------------


def test_mark_messages_read(client, test_user, auth_headers, test_company):
    """PUT /companies/{id}/messages/read marks admin messages as read."""
    response = client.put(
        f"/api/v1/companies/{test_company.id}/messages/read",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "marked_read" in data
    assert isinstance(data["marked_read"], int)


def test_mark_messages_read_requires_auth(client, test_company):
    """PUT /companies/{id}/messages/read without auth returns 401."""
    response = client.put(
        f"/api/v1/companies/{test_company.id}/messages/read",
    )
    assert response.status_code == 401


def test_mark_messages_read_wrong_company(client, test_user, auth_headers):
    """PUT messages/read for non-owned company returns 404."""
    response = client.put(
        "/api/v1/companies/99999/messages/read",
        headers=auth_headers,
    )
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Wrong Company Access
# ---------------------------------------------------------------------------


def test_send_message_wrong_company(client, test_user, auth_headers):
    """POST message for non-owned company returns 404."""
    response = client.post(
        "/api/v1/companies/99999/messages",
        json={"content": "Nope"},
        headers=auth_headers,
    )
    assert response.status_code == 404


def test_list_messages_wrong_company(client, test_user, auth_headers):
    """GET messages for non-owned company returns 404."""
    response = client.get(
        "/api/v1/companies/99999/messages",
        headers=auth_headers,
    )
    assert response.status_code == 404
